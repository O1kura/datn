# MCQ Generation System from Images

This project is designed to generate multiple-choice questions (MCQs) from images. The system processes the images, extracts text, and creates MCQs from the extracted data. This README file will guide you through the steps required to set up and run the project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Step 1: Install Virtual Environment](#step-1-install-virtual-environment)
  - [Step 2: Install Dependencies](#step-2-install-dependencies)
  - [Step 3: Create Configuration File](#step-3-create-configuration-file)
  - [Step 4: Install Tesseract](#step-4-install-esseract)
- [Running the Project](#running-the-project)
- [License](#license)

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- Python 3.8 or higher
- pip (Python package installer)

## Setup Instructions

### Step 1: Install Virtual Environment

To avoid conflicts with other projects and maintain a clean development environment, it is recommended to use a virtual environment, `anaconda` or `virtualenv`.
Steps below for using `virtualenv`

1. **Install `virtualenv`**:

    ```bash
    pip install virtualenv
    ```

2. **Create a Virtual Environment**:

    ```bash
    virtualenv venv
    ```

3. **Activate the Virtual Environment**:

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

### Step 2: Install Dependencies

With the virtual environment activated, install the required dependencies using the provided `requirements.txt` file.

1. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

### Step 3: Create Configuration File

Create a `config.py` file in the project directory with the necessary configuration values for the database and other settings.

1. **Create `config.py`**:

    ```python
    # config.py

    mysql_db_name = your_db_name
    mysql_user = yoursql_user
    mysql_pass = yoursql_pass
    mysql_host = yoursql_host
    mysql_port = yoursql_port
    tesseract_OCR = your_tesseract_OCR_path
    watermark_img_path = 'static/watermark/watermark.png' 
    mail_username = your_mail_username
    mail_password = your_mail_password
    mail_port = 587
    mail_use_ssl = False
    mail_use_tls = True
    thumb_size = 1920
    thumbs_dir = 'thumbnails'
    run_port = your_run_port
    log_file = your_log_file_path
    ```

    Replace the placeholder values with your actual database credentials and any other necessary settings.
### Step 4: Install Tesseract
1. **Install Tesseract-OCR**:

    - On Windows, download and install Tesseract from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).

    - On macOS, you can use Homebrew:

        ```bash
        brew install tesseract
        ```

    - On Ubuntu:

        ```bash
        sudo apt-get install tesseract-ocr
        ```

For more details on installing `pytesseract`, visit the [pytesseract GitHub page](https://github.com/madmaze/pytesseract).

## Running the Project

With the setup complete, you can now run the project.

1. **Apply Migrations**:

    ```bash
    python manage.py migrate
    ```

2. **Start the Development Server**:

    ```bash
    python manage.py runserver
    ```

3. **Access the Application**:

    The system is listening on default port 8000 of Django. Requests to `http://127.0.0.1:8000/` to access the application.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to reach out if you encounter any issues or have any questions!
