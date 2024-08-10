import mysql.connector

# Establish a connection to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@Nilesh.Tiwari1",
    database="environmental_data"

)


#!Create Table
# # Create a cursor object
# cursor = conn.cursor()

# # SQL query to create the table
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS materials (
#     material_name VARCHAR(255) PRIMARY KEY,
#     pollution_index FLOAT
# )
# """)

# # Commit the changes and close the connection
# conn.commit()
# cursor.close()
# conn.close()




#! Insert data
# cursor = conn.cursor()


# insert_query = "INSERT INTO materials (material_name, pollution_index) VALUES (%s, %s)"
# cursor.execute(insert_query, ("Iron", "20"))
# conn.commit()
# print("Data inserted successfully")



#! Read data

material_name = input(str("Enter the item name: "))

def environment_database(material_name:str):
    cursor = conn.cursor()
    query = "SELECT pollution_index FROM materials WHERE material_name = %s"
    cursor.execute(query, (material_name.lower(),))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else "Not found use search tool"
    



