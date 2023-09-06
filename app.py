from flask import Flask, render_template, request, redirect, url_for
from scraper import HasznaltautoScraper
from model import CarPriceModel
from plotter import PredictedPricePlot

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        input_link = request.form['input_link']

        scraper_obj = HasznaltautoScraper(input_link)
        scraped_df = scraper_obj()

        car_price_model_obj = CarPriceModel(scraped_df)
        predicted_df = car_price_model_obj()

        predicted_price_plot_obj = PredictedPricePlot()
        plot_html_str = predicted_price_plot_obj(predicted_df)
        

        return render_template('result.html', input_link=input_link, plot=plot_html_str)

if __name__ == '__main__':
    app.run(debug=True)
