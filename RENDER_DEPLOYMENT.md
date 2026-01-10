# Deploying HRMS to Render

This guide will help you deploy the HRMS Django application to Render.

## Prerequisites

1. A GitHub account with your HRMS repository pushed to GitHub
2. A Render account (sign up at [render.com](https://render.com) if you don't have one)

## Step 1: Create a PostgreSQL Database on Render

1. Log in to your Render dashboard
2. Click **New +** → **PostgreSQL**
3. Configure your database:
   - **Name**: `hrms-db` (or any name you prefer)
   - **Database**: `hrms_db`
   - **User**: Auto-generated
   - **Region**: Choose closest to your users
   - **Plan**: Free tier is fine for development
4. Click **Create Database**
5. **Important**: Copy the **Internal Database URL** or **External Database URL** - you'll need this later

## Step 2: Create a Web Service on Render

1. In your Render dashboard, click **New +** → **Web Service**
2. Connect your GitHub repository:
   - Click **Connect GitHub** if not already connected
   - Select your HRMS repository
   - Click **Connect**
3. Configure your service:
   - **Name**: `hrms-django` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Region**: Same region as your database
   - **Branch**: `main` (or your main branch)
   - **Root Directory**: Leave blank (if root) or specify if your Django project is in a subdirectory
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate
     ```
   - **Start Command**:
     ```bash
     gunicorn hrms_project.wsgi:application
     ```
   - **Plan**: Free tier is fine for development

## Step 3: Configure Environment Variables

In your Web Service settings, go to **Environment** section and add these environment variables:

### Required Environment Variables:

1. **SECRET_KEY**: 
   - Generate a new secret key for production (DO NOT use the development key)
   - You can generate one using:
     ```python
     from django.core.management.utils import get_random_secret_key
     print(get_random_secret_key())
     ```
   - Or use an online Django secret key generator

2. **DEBUG**: 
   - Value: `False` (for production)
   - This disables debug mode

3. **ALLOWED_HOSTS**: 
   - Value: `your-app-name.onrender.com`
   - Replace `your-app-name` with your actual Render service name
   - If you have a custom domain, add it like: `your-app-name.onrender.com,yourdomain.com`

4. **DATABASE_URL**: 
   - This should be automatically set by Render if you linked the PostgreSQL database
   - If not automatically set, use the database URL from Step 1
   - Format: `postgresql://user:password@host:port/database`

### Example Environment Variables:

```
SECRET_KEY=django-insecure-your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=hrms-django.onrender.com
DATABASE_URL=postgresql://user:password@hostname:5432/hrms_db
```

## Step 4: Link PostgreSQL Database to Web Service

1. In your Web Service settings, go to **Environment** section
2. Scroll down to **Add Environment Variable from Database**
3. Select your PostgreSQL database
4. The `DATABASE_URL` will be automatically added

## Step 5: Deploy

1. Click **Create Web Service**
2. Render will automatically:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Run build commands
   - Collect static files
   - Run migrations
   - Start your application with gunicorn

3. Wait for the deployment to complete (usually takes 5-10 minutes for first deployment)

4. Once deployed, you'll see a URL like: `https://hrms-django.onrender.com`

## Step 6: Create a Superuser (Optional)

To access the Django admin panel, you need to create a superuser:

1. In your Render dashboard, go to your Web Service
2. Click on **Shell** tab (or use **Logs** to see output)
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow the prompts to create your admin account
5. Access admin at: `https://your-app-name.onrender.com/admin/`

## Troubleshooting

### Static files not loading:
- Ensure `collectstatic` is running in the build command
- Check that `STATIC_ROOT` is set correctly in settings.py
- Verify WhiteNoise is properly configured

### Database connection errors:
- Verify `DATABASE_URL` is correctly set
- Ensure PostgreSQL database is running
- Check that database credentials are correct

### 500 errors:
- Check the logs in Render dashboard
- Ensure `DEBUG=False` and `ALLOWED_HOSTS` is set correctly
- Verify all environment variables are set

### Migration errors:
- Run `python manage.py migrate` manually in the Shell
- Check that all migration files are committed to git

## Files for Render Deployment

The following files have been configured for Render:

- **Procfile**: Defines the web process (gunicorn)
- **build.sh**: Build script (optional, can use build command in Render dashboard)
- **requirements.txt**: Python dependencies including production packages
- **settings.py**: Updated for production with environment variables

## Post-Deployment

1. **Test your application**: Visit your Render URL and test all features
2. **Monitor logs**: Check Render dashboard logs for any errors
3. **Set up custom domain** (optional): Configure a custom domain in Render settings
4. **Enable HTTPS**: Render provides free SSL certificates automatically

## Cost

- **Free Tier**: 
  - 750 hours/month for web services
  - Free PostgreSQL database (90 days, then $7/month)
  - Services sleep after 15 minutes of inactivity (free tier)
  - Perfect for development and testing

- **Paid Plans**: Starting at $7/month for always-on web services

## Additional Resources

- [Render Django Deployment Guide](https://render.com/docs/deploy-django)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render PostgreSQL](https://render.com/docs/databases)

