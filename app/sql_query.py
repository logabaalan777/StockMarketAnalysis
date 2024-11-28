from pyspark.sql import SparkSession
import streamlit as st

def execute_sql_query(data):
    spark = SparkSession.builder.appName("SQLExecution").getOrCreate()
    df = spark.createDataFrame(data)
    df.createOrReplaceTempView("stocks")

    st.write("**Available Columns for Query:**", list(data.columns))

    query = st.text_area("Enter your SQL Query (Use 'stocks' as the table name)")
    if st.button("Run Query"):
        try:
            query_result = spark.sql(query)
            result_df = query_result.toPandas()
            st.write("**Query Results:**")
            st.dataframe(result_df)
        except Exception as e:
            st.error(f"Error: {e}")
