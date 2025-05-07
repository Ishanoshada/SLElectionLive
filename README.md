
# SLElectionLive

![SLElectionLive Dashboard](https://img.shields.io/badge/Flask-3.0.3-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub Issues](https://img.shields.io/github/issues/Ishanoshada/SLElectionLive)

**SLElectionLive** is a Flask-based web application that provides real-time election results for Sri Lanka. It features an interactive dashboard with charts, a live news stream, and an SMS campaign interface. The application scrapes data from `results.elections.gov.lk` and uses Chart.js for visualizations, Bootstrap for styling, and a responsive design for accessibility across devices.

![img1](https://github.com/Ishanoshada/Ishanoshada/blob/main/ss2/Screenshot%202025-05-07%20203443.png?raw=true)


## Table of Contents
- [Live Demo](#live-demo)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Attribution](#attribution)


## Live Demo
Explore the live application at [https://sl-election-live.vercel.app/](https://sl-election-live.vercel.app/). View real-time election results, news updates, and manage SMS campaigns. 

![img2](https://github.com/Ishanoshada/Ishanoshada/blob/main/ss2/Screenshot%202025-05-07%20201414.png?raw=true)

## Features
- **Live Election Results Dashboard**: Displays vote shares, seats, and party details with an interactive doughnut chart.
- **Real-Time News Stream**: Fullscreen news mode with voter turnout, social sharing, and automatic updates every 30 seconds.
- **SMS Campaign Interface**: Manage and send SMS campaigns for election updates.
- **Dark Mode**: Toggle between light and dark themes for better usability.
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices.
- **Data Scraping**: Fetches live election data from `results.elections.gov.lk` using BeautifulSoup.
- **Fallback Data**: Uses sample data when API or scraping fails, ensuring uninterrupted service.

## Project Structure
```
SLElectionLive/
├── api/
│   ├── app.py               # Flask application with routes and scraping logic
│   ├── sample_data.py       # Generates sample election data for fallback
│   ├── templates/
│   │   ├── index.html       # Election results dashboard
│   │   ├── news.html        # Live news stream page
│   │   ├── sms_campaign.html # SMS campaign interface
├── packages.json            # Node.js configuration (optional for Vercel)
├── requirements.txt         # Python dependencies
├── test.py                  # Test script for development
├── vercel.json              # Vercel deployment configuration
├── README.md                # This file
```


## Installation
Follow these steps to set up the project locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Ishanoshada/SLElectionLive.git
   cd SLElectionLive
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory:
     ```bash
     touch .env
     ```
   - Add necessary configurations (e.g., API keys, if used):
     ```plaintext
     FLASK_ENV=development
     SECRET_KEY=your_secret_key
     ```

6. **Run the Application**:
   ```bash
   python api/app.py
   ```
   - The app will be available at `http://localhost:5000`.

## Usage
- **Dashboard (`/`)**: View the latest election results with a chart and table of party details.
- **News Stream (`/news`)**: Access live updates with voter turnout, social sharing buttons, and navigation for recent results.
- **SMS Campaign (`/sms_campaign`)**: Manage SMS campaigns for election notifications.
- **Dark Mode**: Click the moon/sun icon in the navbar to toggle themes.
- **Fullscreen Mode**: On the news page, click the fullscreen button for an immersive view.

To test with sample data:
- Modify `app.py` to force `use_sample_data=True` or simulate a failed API call.

## Deployment
### Local Deployment
- Use `gunicorn` for production-like local testing:
  ```bash
  gunicorn -w 4 -b 0.0.0.0:8000 api.app:app
  ```

### Vercel Deployment
The project includes `vercel.json` and `packages.json`, suggesting Vercel compatibility. To deploy:
1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```
2. Deploy from the project root:
   ```bash
   vercel
   ```
3. Follow prompts to configure the project (ensure `api/app.py` is the entry point).
4. Update `vercel.json` if needed to map routes correctly.

### Other Platforms
- **Heroku**: Push to a Heroku app with `Procfile`:
  ```plaintext
  web: gunicorn api.app:app
  ```
- **Render**: Configure as a Python web service with `requirements.txt`.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request on `https://github.com/Ishanoshada/SLElectionLive`.

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md) and include tests in `test.py` for new features.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Attribution
- **Created by**: [Ishanoshada](https://github.com/Ishanoshada)
- **Source Code**: [https://github.com/Ishanoshada/SLElectionLive](https://github.com/Ishanoshada/SLElectionLive)
- **Data Source**: [results.elections.gov.lk](https://results.elections.gov.lk)



![Views](https://dynamic-repo-badges.vercel.app/svg/count/6/Repository%20Views/slelectionlive)