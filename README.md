# My Flask Project

## Setup

1. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up the database:
    ```sh
    flask db upgrade
    ```

4. Run the application:
    ```sh
    python run.py
    ```

## Testing

Run the tests using:
```sh
python -m unittest discover tests
