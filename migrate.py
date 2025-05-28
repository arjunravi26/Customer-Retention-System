import subprocess

subprocess.run([
    r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",  # ✅ Full path to the executable
    "-U", "postgres",                                   # ✅ Replace with your actual DB username
    "-d", "telcom",                                     # ✅ Your database name
    "-f", "telcom.sql"                                  # ✅ Output file name
])

