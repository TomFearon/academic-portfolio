# Import necessary modules
import sqlite3 as sql

# Procedure to create tables in the database
def create_table(tableName, fields):
    # Open database file
    database = sql.connect("Database.db")

    # Create a cursor to run sql commands
    cursor = database.cursor()

    # Table layout will be formatted so that it can be passed as an argument to create the table
    tableLayout = tableName + " (id INTEGER PRIMARY KEY AUTOINCREMENT" # First field in the table will be the primary key
    # Formats all fields passed into procedures and adds them to the layout
    for field in fields: 
        tableLayout = tableLayout + ", "
        fieldName = field[0]
        fieldDataType = field[1]
        tableLayout = tableLayout + fieldName + " " + fieldDataType
    # End of table layout definition
    tableLayout = tableLayout + ")"

    # Creates sql command with concatenated table layout
    tableCreation = "CREATE TABLE IF NOT EXISTS " + tableLayout
    # Executes the command, creating the table
    cursor.execute(tableCreation)

    # Saves changes to database and closes connection
    database.commit()
    database.close()

# Procedure to insert records into given table
def insert_query(tableName, instructions):
    # Open database file
    database = sql.connect("Database.db")

    # Create a cursor to run sql commands
    cursor = database.cursor()

    # Collects fields info from table
    cursor.execute(f"PRAGMA table_info({tableName})")
    fields = cursor.fetchall()

    # Iterates through 'fields', appending the name of the column to the list 'fieldNames'
    fieldNames = []
    # Skips first field, as this will always be id - which will not be passed into function
    for i in range(1, len(fields)):
        fieldNames.append(fields[i][1])
    
    # Inserts each record into the table 
    for record in instructions:
        # Cancels operations if number of fields in record passed into function is invalid
        if len(record) != len(fieldNames):
            print(f"Error: {record} has an invalid number of fields.")
            # Closes database, not saving any operations ucrrently completed by this function
            database.close()
            return

        # Inserts the record into the table, by creating and passing an sql command
        cursor.execute(f"INSERT INTO {tableName} ({str(fieldNames)[1:][:-1]}) VALUES ({str(record)[1:][:-1]})")
    
    # Save changes to database and close connection
    database.commit()
    database.close()

# Function to select and read information from tables in the database
def select_query(tableName, instructions):
    # Open database file
    database = sql.connect("Database.db")

    # Create a cursor to run sql commands
    cursor = database.cursor()

    # Checks whether index 0 of 'instructions' is an array of fields for the procedure to select
    selectedFields = instructions[0]
    if not isinstance(selectedFields, list):
        # If there is no array at index 0, connection to database will be close and procedure will halt
        print("Error: no selected fields array provided.")
        database.close()
        return
    
    # Formats selected field as string to be used in sql command
    selectedFieldsFormat = f"{selectedFields[0]}"
    if len(selectedFields) > 1:
        for i in range(1,len(selectedFields)):
            selectedFieldsFormat = selectedFieldsFormat + f", {selectedFields[i]}"

    # Creates sql command to select certain fields from records form the table
    command = f"SELECT {selectedFieldsFormat} FROM {tableName} "

    # Adds contsraints to command if constraints are passed into procedure
    if len(instructions) > 1:
        command = command + f"WHERE {instructions[1]} "
        for i in range(2,len(instructions)):
            command = command + f"AND {instructions[i]}"
    
    # Executes select command
    cursor.execute(command)
    # Fetches selected data
    data = cursor.fetchall()

    # Closes connection to database
    database.close()

    # Returns selected data
    return data

# Procedure to update records in tables in the database
def update_query(tableName, instructions):
    # Open database file
    database = sql.connect("Database.db")

    # Create a cursor to run sql commands
    cursor = database.cursor()

    # Assigns update records
    updatedRecords = instructions
    
    # Collects fields info from table
    cursor.execute(f"PRAGMA table_info({tableName})")
    fields = cursor.fetchall()

    # Iterates through 'fields', appending the name of the column to the list 'fieldNames'
    fieldNames = []
    for i in range(0, len(fields)):
        fieldNames.append(fields[i][1])
    
    # Iterate through all records to update
    for i in range(0,len(updatedRecords)):
        # Assigns the updated record and id of it
        record = updatedRecords[i]
        id = record[0]

        #Creates initial command for updating record
        command = f"UPDATE {tableName} SET "
        
        # Checks whether the passed record has valid number of fields
        if len(fieldNames) != len(record):
            print(f"Error: {record} has an invalid number of fields.")
            # Closes connection to database and closes without saving procedure's current changes
            database.close()
            return
        
        # Formats fields with updated values, so that record can be updated
        # 'id' (the field at index 0) is not updated - as this should remain the same
        command = command + f'{fieldNames[1]} = "{str(record[1])}"'
        if len(record) > 1:
            for j in range(2, len(fieldNames)):
                command = command + f', {fieldNames[j]} = "{record[j]}"'
        
        # Creates the final command to update the record of the given id with the given values
        command = command + f" WHERE id = {id}"

        # Executes the command
        cursor.execute(command)

    # Save changes to database and close connection
    database.commit()
    database.close()

# Procedure to delete records from tables in the database
def delete_query(tableName, instructions):
    # Open database file
    database = sql.connect("Database.db")

    # Create a cursor to run sql commands
    cursor = database.cursor()

    # Deletes record at given ids
    for id in instructions:
        cursor.execute(f"DELETE FROM {tableName} WHERE id = {id}")
    
    # Save changes to database and close connection
    database.commit()
    database.close()

# Procedure to delete table in the database
def delete_table(tableName):
    # opens the database file
    database = sql.connect("Database.db")

    # Creates cursor to run sql commands
    cursor = database.cursor()

    # Deletes the table
    cursor.execute(f"DROP TABLE IF EXISTS {tableName}")

    # Save changes to database and close connection
    database.commit()
    database.close()

