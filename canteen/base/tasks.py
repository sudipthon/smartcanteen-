from celery import shared_task
from .models import CustomUser, Student, Course, Administration
import pandas as pd
from django.db import IntegrityError
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task
def add_users_task(file_path, user_type):
    # data = pd.read_excel(file_path, engine="openpyxl")
    _, file_extension = os.path.splitext(file_path)
    if file_extension == ".csv":
        data = pd.read_csv(file_path)
    elif file_extension == ".tsv":
        data = pd.read_csv(file_path, sep="\t")
    else:  # Assume Excel format
        data = pd.read_excel(file_path, engine="openpyxl")

    users = []
    error_users = []

    for _, row in data.iterrows():
        try:
            user = CustomUser(
                college_id=row["ID"],
                username=row["Name"],
                password=row["Password"],
            )
            user.save()  # save the user to generate an ID
            users.append(user)

            if user_type == "Student":
                course = Course.objects.get(name=row["Course"])
                student = Student(
                    user=user,
                    semester=row["Semester"],
                    course=course,
                )
                student.save()
            else:
                admin = Administration(
                    user=user,
                    user_type=user_type,
                )
                admin.save()
        except Exception as e:
            error_users.append(row["Name"])
            # error_info = row.to_dict()
            # error_info["Error"] = str(e)
            # error_users.append(error_info)


        with open("error_users.txt", "w") as f:
            f.write("\n".join(error_users))

#   # Write error users to an Excel file if there are any
#     if error_users:
#         error_df = pd.DataFrame(error_users)
#         error_df.to_excel("error_users.xlsx", index=False)