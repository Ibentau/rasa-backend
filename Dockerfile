FROM rasa/rasa:3.3.1-full

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Make port 5005 available to the world outside this container
EXPOSE 5005

# Run app.py when the container launches
CMD ["run", "-m", "models", "--enable-api", "--cors", "*"]
