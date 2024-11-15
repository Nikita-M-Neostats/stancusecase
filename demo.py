import csv
import psycopg2
from psycopg2 import Error

try:
    connection = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="root",
        port="5432"
    )

    cursor = connection.cursor()

    csv_file_path = r"C:\Users\Nikita.Mate\StanC\StandardC\account_details1.csv"

    # First, execute the CREATE TABLE query to create the table structure
    query1 = """
    CREATE TABLE account_details (
        account_no VARCHAR(50),
        current_flag CHAR(1),
        days_30_flag CHAR(1),
        days_60_flag CHAR(1),
        days_90_flag CHAR(1),
        flag_90 CHAR(1),
        del_30 CHAR(1),
        disbursement_date VARCHAR(50),
        gov_non_gov VARCHAR(50),
        teller_name VARCHAR(100),
        product VARCHAR(50),
        arrears_rpmt_days_ifrs9 VARCHAR(100),
        last_paid_date VARCHAR(50),
        sales_person_id2 VARCHAR(50),
        sales_person_name2 VARCHAR(255),
        account_status VARCHAR(100),
        loan_balance DECIMAL(18,2),
        cat INT,
        country VARCHAR(50),
        broker_no VARCHAR(100),
        broker_name VARCHAR(255),
        designation VARCHAR(100),
        branch_no VARCHAR(50),
        branch_name VARCHAR(255),
        region VARCHAR(50),
        team_leader VARCHAR(255),
        team_leader_code VARCHAR(255),
        branch_manager VARCHAR(255),
        branch_manager_code VARCHAR(255),
        regional_manager VARCHAR(255),
        regional_manager_code VARCHAR(255),
        pulaadjustment DECIMAL(18,2),
        ageband VARCHAR(100),
        accountnonew VARCHAR(255),
        neverpaid CHAR(1),
        first_repay_date VARCHAR(50),
        acc_no VARCHAR(255),
        first_default_1 CHAR(1),
        loan_balance_bwp DECIMAL(18,2),
        current_bal DECIMAL(18,2),
        days_30_bal DECIMAL(18,2),
        days_60_bal DECIMAL(18,2),
        days_90_bal DECIMAL(18,2),
        plus_90_days_bal DECIMAL(18,2),
        current_bal_bwp DECIMAL(18,2),
        days30_bal_bwp DECIMAL(18,2),
        days60_bal_bwp DECIMAL(18,2),
        days90_bal_bwp DECIMAL(18,2),
        plus90_days_bal_bwp DECIMAL(18,2),
        never_paid_bal DECIMAL(18,2),
        never_paid_bal_bwp DECIMAL(18,2),
        disbursement_afterapr22 CHAR(1),
        disb_month1 DATE,
        first_payment_default_bal DECIMAL(18,2),
        first_payment_default_bal_bwp DECIMAL(18,2),
        new_current CHAR(1),
        reportdatekey_lc VARCHAR(50),
        employer_name VARCHAR(255),
        employer_type VARCHAR(50),
        store_rate DECIMAL(18,2),
        loan_amount_disbursed DECIMAL(18,2),
        loan_trm INT
    );
    """
    cursor.execute(query1)

    # Read and insert data from the CSV file
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row

        insert_query = "INSERT INTO account_details VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        for row in reader:
            cursor.execute(insert_query, row)

    connection.commit()
    print("Data inserted successfully!")

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:
    if 'connection' in locals():
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

