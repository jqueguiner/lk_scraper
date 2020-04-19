FROM python:3.7
RUN pip install git+https://github.com/Hugoch/lk_scraper.git
CMD ["python"]
