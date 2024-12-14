# Server Instructions 🏃

## Starting the Server
To run the server, execute the following command:
```
python.exe main.py
```

## API Endpoints 🔹🔚

### 1. **`/login/<user_id>`**
- **Description:** Initiates a session for the specified user.
- **Functionality:**
  - Creates a new file or opens an existing one to store user data.

### 2. **`/measurements`**
- **Description:** Retrieves user data for the currently logged-in user.
- **Response Format:** JSON dictionary containing the user's data.

### 3. **`/predict/<user_id>`**
- **Description:** Provides the current mental health status of the specified user.
- **Possible Labels:**
  - **baseline** (normal)
  - **stress**
  - **amusement**
  - **meditation**

## Data Generation and Persistence
- **Frequency of Data Generation:** A new pair of data points is generated in memory every 2 seconds.
- **Data Saving Mechanism:**
  - The in-memory data list is saved to a file every 60 seconds.

This ensures continuous monitoring and efficient data handling.

