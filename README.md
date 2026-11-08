# Student Exam Performance Prediction

Flask application that predicts a student's math score from exam and demographic inputs.

## Deploy to AWS

The AWS infrastructure template is `infra/codepipeline.yml`. It creates a GitHub-triggered CodePipeline that builds and deploys this Flask application to an **existing** Elastic Beanstalk environment.

### What the cloud infrastructure does

1. **GitHub connection and CodePipeline:** CodePipeline watches the configured repository and branch through an AWS CodeStar connection (also called a CodeConnections connection in some AWS consoles).
2. **Build and model training:** CodeBuild installs the pinned Python dependencies, trains the model from `notebook/data/stud.csv`, and smoke-tests the prediction route. Training regenerates `artifact/model.pkl` and `artifact/preprocessor.pkl`; these files are deliberately excluded from Git.
3. **Artifact storage:** An encrypted, private S3 bucket created by the CloudFormation stack stores the pipeline's source and build artifacts.
4. **Application deployment:** The build output includes the Flask application, generated model artifacts, templates, dependencies, `Procfile`, and `.ebextensions` configuration. CodePipeline deploys that bundle to the specified Elastic Beanstalk application and environment. Elastic Beanstalk runs the app with Gunicorn.
5. **Access control:** CloudFormation creates IAM roles for CodePipeline and CodeBuild with permissions for the pipeline's source, build, storage, and deployment actions.

The template creates the S3 bucket, IAM roles, CodeBuild project, and CodePipeline. It does **not** create the Elastic Beanstalk application/environment or GitHub connection; create those first.

### Prerequisites

- An AWS account and AWS CLI configured with credentials for the correct account and region.
- Permission to create CloudFormation stacks, IAM roles/policies, S3 buckets, CodeBuild projects, and CodePipeline pipelines. The deploying identity may need permission to pass the generated service roles.
- A GitHub repository containing this project and an Elastic Beanstalk **Python** application/environment in the same AWS region as the pipeline.
- An AWS CodeStar/CodeConnections connection to GitHub, created in that region. Its status must be **Available** before the pipeline can retrieve source.

### Deployment steps

1. **Create the Elastic Beanstalk target.** In the AWS console, create an Elastic Beanstalk application and a Python web server environment. Configure the environment's instance profile and service role as required by your account. Record the exact application and environment names. The app's WSGI entry point is `application:application`, configured in `.ebextensions/python.config`; `Procfile` starts Gunicorn on port 8000.
2. **Create the GitHub connection.** In the AWS console, open Developer Tools / Connections (the label may vary), create a connection to GitHub, and complete its GitHub authorization/install flow. Copy the connection ARN after its status becomes **Available**.
3. **Create the pipeline stack.** From the repository root, run the following command, replacing the three placeholder values with your connection ARN and exact Elastic Beanstalk names:

   ```sh
   aws cloudformation deploy \
     --template-file infra/codepipeline.yml \
     --stack-name student-performance-pipeline \
     --capabilities CAPABILITY_IAM \
     --parameter-overrides \
       GitHubConnectionArn=arn:aws:codeconnections:REGION:ACCOUNT_ID:connection/CONNECTION_ID \
       EBApplicationName=YOUR_EB_APPLICATION \
       EBEnvironmentName=YOUR_EB_ENVIRONMENT
   ```

   The template defaults the GitHub repository to `codecmy/MLprojects` and branch to `main`. For a fork or another branch, add `GitHubOwner=YOUR_OWNER`, `GitHubRepository=YOUR_REPOSITORY`, or `BranchName=YOUR_BRANCH` to `--parameter-overrides`. Use the connection ARN shown in your AWS account; older connections may use the `codestar-connections` ARN prefix.
4. **Check the first run.** In the CloudFormation stack outputs, copy the generated `PipelineName` and open that pipeline in AWS CodePipeline to inspect the Source, Build, and Deploy stages. (The CloudFormation stack is named `student-performance-pipeline`; AWS generates a separate physical pipeline name.) The first run may require the connection to be authorized/activated in the AWS console. A successful deployment updates the selected Elastic Beanstalk environment.
5. **Open the application.** Find the environment URL in the Elastic Beanstalk console and visit it. Push a commit to the configured branch to trigger subsequent build-and-deploy runs.

### Build and runtime configuration

`buildspec.yml` defines the CodeBuild install, training, smoke-test, and artifact packaging steps. `requirements.txt` pins the dependencies used both to train and to load the serialized model, avoiding scikit-learn version mismatches. The generated model files are packaged from CodeBuild output rather than committed to the repository.

To remove the pipeline resources created by this template, delete the `student-performance-pipeline` CloudFormation stack. This does not delete the separately managed Elastic Beanstalk environment or GitHub connection. Confirm the stack's contents and any remaining S3 artifacts before deleting resources.