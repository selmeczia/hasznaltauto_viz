from flask import Flask, render_template, request, redirect, url_for, session, abort
from hasznaltauto_scraper.scraper import HasznaltautoScraper
from hasznaltauto_scraper.model import CarPriceModel
from hasznaltauto_scraper.plotter import PredictedPricePlot
from hasznaltauto_scraper.data_validation import DataValidator
import time
import os
from applicationinsights import TelemetryClient


app = Flask(__name__)
app.secret_key = os.urandom(24)
appinsights = TelemetryClient(os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY'))


@app.route('/')
def index():
    alert_message = session.pop('alert_message', None)

    return render_template('index.html', alert=alert_message)


@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        input_link = request.form['input_link']

        appinsights.track_event("UserSubmitLink", properties={
                                "link": str(input_link)})

        validator = DataValidator(input_link)
        validator.validate_link()

        if validator.is_valid():
            start_time = time.time()
            scraper_obj = HasznaltautoScraper(input_link)
            scraped_df = scraper_obj()
            end_time = time.time()

            appinsights.track_metric(
                "ScrapingTime", end_time-start_time, properties={"PageCount": scraper_obj.last_page})

            start_time = time.time()
            car_price_model_obj = CarPriceModel(scraped_df)
            predicted_df = car_price_model_obj()
            end_time = time.time()
            appinsights.track_metric("ModelTime", end_time-start_time)

            start_time = time.time()
            predicted_price_plot_obj = PredictedPricePlot()
            plot_html_str = predicted_price_plot_obj(predicted_df)
            end_time = time.time()
            appinsights.track_metric("PlotTime", end_time-start_time)

            return render_template('result.html', input_link=input_link, plot=plot_html_str)

        else:
            appinsights.track_exception()

            session['alert_message'] = 'Hibás link!'
            return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(error):
    title = "A keresett oldal nem található"
    return render_template('error.html', status_code=404, title=title), 404


@app.errorhandler(500)
def internal_error(error):
    title = "A szerveren valamilyen hiba lépett fel"
    return render_template('error.html', status_code=500, title=title), 500


@app.after_request
def after_request(response):
    appinsights.flush()
    return response


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
