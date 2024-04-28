import streamlit as st
import mysql.connector
import pandas as pd

def connect_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='1234',
        database='ninad1'
    )
    return conn

def create_books_table():

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Name VARCHAR(255),
            Author VARCHAR(255),
            Genre VARCHAR(10),
            Quantity INT
            
        );
    """)
    conn.commit()
    conn.close()

def insert_books(Name,Author,Genre,Quantity):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO books (Name,Author,Genre,Quantity)
        VALUES (%s, %s, %s, %s);
    """, (Name,Author,Genre,Quantity))
    conn.commit()
    conn.close()

def fetch_books():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books_data = cursor.fetchall()
    conn.close()
    return books_data

def user_login(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT clg_id FROM users WHERE student_name = %s", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0] == password
    return False

def create_user_books_table(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {username}_books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_name VARCHAR(255),
            author VARCHAR(255),
            genre VARCHAR(10),
            assign_date DATE,
            return_date DATE
        );
    """)
    conn.commit()
    conn.close()

def create_book_requests_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_requests (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255),
        book_name VARCHAR(255),
        assign_date DATE,
        return_date DATE
        );
        """)
    conn.commit()
    conn.close()

def assign_book(username, book_name,assign_date,return_date):
    conn = connect_db()
    cursor = conn.cursor()

    
    cursor.execute("UPDATE books SET Quantity = Quantity - 1 WHERE Name = %s", (book_name,))

   
    cursor.execute("SELECT author, genre FROM books WHERE Name = %s", (book_name,))
    book_data = cursor.fetchone()

    
    cursor.execute(f"""
        INSERT INTO {username}_books (book_name, author, genre, assign_date, return_date)
        VALUES (%s, %s, %s, %s, %s)
        """, (book_name, book_data[0], book_data[1],assign_date,return_date))
    
    st.success("Book assigned successfully!")

    
    cursor.execute("DELETE FROM book_requests WHERE book_name = %s", (book_name,))
        
    conn.commit()
    conn.close()



def display_book_requests():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM book_requests")
    requests_data = cursor.fetchall()
    conn.close()
    return requests_data

def make_book_request(username, book_name, assign_date, return_date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO book_requests (username, book_name, assign_date, return_date)
        VALUES (%s, %s, %s, %s);
    """, (username, book_name, assign_date, return_date))
    conn.commit()
    conn.close()

def fetch_user_books(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {username}_books")
    user_books_data = cursor.fetchall()
    conn.close()
    return user_books_data

def main():
    st.title("Library")

    create_books_table()
    create_book_requests_table()

    selection = st.sidebar.radio("Navigation", ["User", "Admin"])

    if selection == "Admin":
        st.header("Admin Panel")
        password = st.text_input("Enter Admin Password", type="password")
        
        if password == "admin1234":

            st.header("Add Books")

            Name = st.text_input("Name")
            Author = st.text_input("Author")
            Genre = st.text_input("Genre")
            Quantity = st.number_input("Quantity", min_value=0)

            if st.button("Submit"):
                insert_books(Name,Author,Genre,Quantity)
                st.success("User details submitted successfully!")

        st.header("Book Requests")
        requests_data = display_book_requests()
        for request in requests_data:
            st.write(f"Request ID: {request[0]}, Username: {request[1]}, Book Name: {request[2]}, Assign Date: {request[3]}, Return Date: {request[4]}")
            if st.button(f"Assign Book {request[0]}"):
                assign_book(request[1], request[2],request[3],request[4])
                st.success("Book assigned successfully!")

    
    elif selection == "User":
        st.header("User Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if user_login(username, password):
                st.success("Login successful!")

                
        create_user_books_table(username)

        st.header("Books List")
        books_data = fetch_books()
        if books_data:
            df = pd.DataFrame(books_data, columns=['ID', 'Name', 'Author', 'Genre', 'Quantity'])
            st.dataframe(df)
        else:
            st.write("No books available.")

        st.header("Make Book Assignment Request")
    
        book_name = st.text_input("Book Name")
        assign_date = st.date_input("Assign Date")
        return_date = st.date_input("Return Date")

        if st.button("Send Request"):
            make_book_request(username, book_name, assign_date, return_date)
            st.success("Request sent successfully!")


        st.header("Assigned Books")
        user_books_data = fetch_user_books(username)
        if user_books_data:
            df = pd.DataFrame(user_books_data, columns=['ID', 'Book Name', 'Author', 'Genre', 'Assign Date', 'Return Date'])
            st.dataframe(df)
        else:
            st.write("No books assigned to this user.")

if __name__ == "__main__":
    main()
