## EDU-TRACK API

-- `if running on your local env`

- clone the project locally with git

  - `git clone https://github.com/Dudeiebot/EduTrack.git`

- change to the project folder

  - `cd edu_track/`

- create a virtual environment for the project

  - `python -m venv env`

- activate the virtual environment

  - `source env/bin/activate`

- run these commands to setup and run the project

  - ```sh
    python3 -m pip install --upgrade pip && pip3 install daphne

    uv pip install -r requirements.txt

    uv pip install psycopg2-binary

    python3 edu_track/manage.py collectstatic --no-input

    python3 edu_track/manage.py create_roles_permission

    python3 edu_track/manage.py runserver
    ```

- there is a `.env` file in `edu_track` and you can add the necessary environment variables

  -- `if you want to run it on a server with docker then`

- add the SSH host and SSH port

- and just run

  - `bash prod-deploy.sh` for prod
  - `bash dev-deploy.sh` for dev

- make sure the `.env` have all the variables added

### Documentation

#### Roles And Permission Scope

- we want a dynamic kind of Roles, so that different roles can be different with different Permission scopes, it goes like this
- The platform supports three key role types: `Instructor`, `Student`, and `System Admin`.
- All users are instances of Django’s user model via `get_user_model()`.
- Actions like `CREATE`, `VIEW`, `UPDATE`, and `DELETE` are treated as core system operations.
- Permissions are assigned to roles, not directly to users.
- System resources are uniquely identified using a `key`.
- Platform actors performing changes are either `SYSTEM` (automated actions) or `USER` (manual actions).
- Roles can be soft-disabled using the `disabled` flag.

- **Role-First Permissioning**: Users receive permissions through their assigned roles. This keeps the system easy to manage and scalable.
- **Separation of Concerns**: `Permission` objects link an `Operation` to a `SystemResource`, allowing for fine-grained access control.
- **Traceability**: Models track `created_by` and `created_by_category` to identify the origin of changes (user or system).
- **Reusability**: Permissions are reusable across roles and can represent actions on any number of domain resources.

- we create the roles and the permission with the resource.json and it is being called when our app is intialized, with the `python3 edu_track/manage.py create_roles_permission
`
- we use the decorator `@permission_required`, call our operation and resource with it, so something like @permission_required("create_course") which can be only done by systemadmin and Instructor

#### User

- The platform uses email as the **primary identifier** for users.
- All users must provide a first and last name during creation.
- Email verification is optional but supported via token validation.
- Passwords are stored using Django’s secure hashing mechanisms (`make_password`, `check_password`).
- A user can have only one role (linked via a separate `UserRole` model).
- Different user types (like `Student` or `Instructor`) can be extended later through **profile models**.
- **Email as Username**: Email is used as the login field (`USERNAME_FIELD = "email"`), which enhances usability and reduces login friction.
- **Flexible Extension**: Instead of cluttering the `User` model, additional data for students, instructors, etc., will be stored in profile models linked via OneToOne relationships.
- **Custom Password Handling**: Overrides `set_password` and `check_password` to align with Django's secure hash system while enabling password reset functionality.
- **Lowercased Emails**: Emails are normalized to lowercase during validation to avoid duplication issues.

##### i can use extensive profile like this

```python
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school_id = models.CharField(max_length=20)
    enrolled_date = models.DateField()

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    office_hours = models.TextField()
```

#### Assignment

- Assignments are tied to a course (`Course` model assumed to exist).
- Only the assignment creator (usually an instructor) can add questions.
- Each assignment has:
  - A title, description, cover image, and duration.
  - A deadline and a number of allowed attempts.
- Students can submit answers once per attempt.
- Scores and pass/fail status are automatically recorded after attempts.

## ✅ Example Usage

```python
# Create assignment
assignment = Assignment.objects.create(
    title="Midterm Quiz",
    course=course,
    created_by=teacher,
    allowed_attempts=2,
    deadline=datetime(2025, 6, 1),
)

# Add questions and options
question = AssignmentQuestion.objects.create(assignment=assignment, text="What is 2+2?")
AssignmentQuestionOption.objects.bulk_create([
    AssignmentQuestionOption(question=question, text="3", is_correct=False),
    AssignmentQuestionOption(question=question, text="4", is_correct=True),
])

# Record an attempt
attempt = AssignmentAttempt.objects.create(user=student, assignment=assignment)
response = UserQuestionResponse.objects.create(
    attempt=attempt,
    question=question,
    selected_option=correct_option,
    is_correct=True,
)

```

