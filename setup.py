from setuptools import setup, find_packages

setup(
    name="smart_ride_ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "opencv-python-headless>=4.8.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "plotly>=5.15.0",
        "scikit-learn>=1.3.0",
        "streamlit>=1.28.0",
        "scipy>=1.11.0",
        "joblib>=1.3.0",
    ],
    python_requires=">=3.9",
)
