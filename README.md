# FriendRequestApp
Installation

Step 1: Clone the Repository

Open your terminal or command prompt.
Navigate to the directory where you want to clone the repository.
Run the following command to clone the repository

Step 2: Navigate to the Project Directory

Open your terminal or command prompt.
Navigate to the project directory using the following command

cd {your_project_name}

Step 3: Create a Virtual Environment (Optional)
If you prefer to isolate dependencies, create a virtual environment using the following command:

python -m venv env

Step 4: Activate the Virtual Environment (Optional)
Activate the virtual environment using the following command (the command may vary depending on your operating system):
On Windows:
.\env\Scripts\activate
On macOS/Linux:
source env/bin/activate

Step 5: Install Dependencies
Install the project's dependencies using the following command
pip install -r requirements.txt

Step 6: Configure the Project
Adjust any necessary configuration settings, such as database credentials or API keys.

Step 7: Run the Project
Start the project using the appropriate command. For example

python manage.py runserver


Step 9: Swagger Documentation

To view the Swagger documentation, start the project and navigate to the following URL in your web browser

http://localhost:8000/swagger

Replace 8000 with the port number specified in your project's configuration.

*NOTE - Swagger provides an interactive API documentation that allows you to explore and test your APIs directly from the browser. This eliminates the need for tools like Postman, as you can easily check and interact with the APIs using Swagger.
