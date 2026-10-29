# SearchSense
Amazon-Style Product Search Engine

## Running the app

```
pip install -r requirements.txt
streamlit run main.py
```

Then open http://localhost:8501. The first run streams 100,000 products from the
Amazon Reviews 2023 dataset, which takes a minute; later runs load from Streamlit's disk cache.
