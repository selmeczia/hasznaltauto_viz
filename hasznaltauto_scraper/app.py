from flask import Flask, render_template, request, redirect, url_for
from hasznaltauto_scraper.scraper import HasznaltautoScraper
from hasznaltauto_scraper.model import CarPriceModel
from hasznaltauto_scraper.plotter import PredictedPricePlot
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        input_link = request.form['input_link']

        start_time = time.time()
        scraper_obj = HasznaltautoScraper(input_link)
        scraped_df = scraper_obj()
        end_time = time.time()
        print(f"Elapsed time for scraping: {end_time-start_time:.4f} seconds")

        start_time = time.time()
        car_price_model_obj = CarPriceModel(scraped_df)
        predicted_df = car_price_model_obj()
        end_time = time.time()
        print(f"Elapsed time for model: {end_time-start_time:.4f} seconds")

        start_time = time.time()
        predicted_price_plot_obj = PredictedPricePlot()
        plot_html_str = predicted_price_plot_obj(predicted_df)
        end_time = time.time()
        print(f"Elapsed time for plot: {end_time-start_time:.4f} seconds")
        

        return render_template('result.html', input_link=input_link, plot=plot_html_str)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
