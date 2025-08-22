# deCONZ Device Viewer 2.0

A modern, optimized web application for viewing and monitoring Zigbee devices from a deCONZ database. Features real-time updates, responsive design, comprehensive error handling, and API endpoints.

## Features

- **Modern UI**: Responsive design with CSS Grid and modern styling
- **Real-time Data**: Automatic device data refresh with caching
- **API Endpoints**: RESTful API for device data and management
- **Error Handling**: Comprehensive error handling and logging
- **Database Integration**: Optimized SQLite queries with connection pooling
- **Configuration**: Environment variable support for flexible deployment
- **Caching**: Intelligent caching system for improved performance
- **Logging**: Structured logging for debugging and monitoring

## Installation

### Prerequisites

- Python 3.8 or higher
- deCONZ gateway with SQLite database
- Virtual environment (recommended)

### Setup

1. **Clone or download the project**:
   ```bash
   cd deconz_viewer
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

## Configuration

### Environment Variables

You can configure the application using environment variables or a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `DECONZ_DB_PATH` | `~/.local/share/deCONZ/zll.db` | Path to deCONZ SQLite database |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode |
| `SECRET_KEY` | `dev-secret-key...` | Flask secret key (change in production) |
| `HOST` | `0.0.0.0` | Server host address |
| `PORT_START` | `8500` | Start of port range for auto-discovery |
| `PORT_END` | `8600` | End of port range for auto-discovery |
| `MAX_DEVICES` | `50` | Maximum number of devices to display |
| `CACHE_TIMEOUT` | `300` | Cache timeout in seconds |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | `deconz_viewer.log` | Log file path |

### Database Path

The application automatically detects the deCONZ database in common locations:
- Linux: `~/.local/share/deCONZ/zll.db`
- Custom path via `DECONZ_DB_PATH` environment variable

## API Endpoints

The application provides RESTful API endpoints:

### Get All Devices
```bash
GET /api/devices
```
Returns all devices with their information.

### Get Device Details
```bash
GET /api/devices/{device_id}
```
Returns detailed information for a specific device.

### Health Check
```bash
GET /api/health
```
Returns application health status and database connectivity.

### Clear Cache
```bash
POST /api/cache/clear
```
Clears the application cache for fresh data.

## Features in Detail

### Performance Optimizations

- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimized SQL queries with proper indexing
- **Caching System**: Intelligent caching with configurable timeouts
- **Lazy Loading**: Resources loaded only when needed

### Error Handling

- **Database Errors**: Graceful handling of database connectivity issues
- **Validation**: Input validation and sanitization
- **Logging**: Comprehensive error logging and monitoring
- **Fallback Queries**: Alternative queries if advanced features fail

### Security

- **Input Validation**: All inputs are validated and sanitized
- **Error Messages**: Secure error messages without sensitive information
- **Configuration**: Secure configuration management

### User Experience

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, intuitive interface with CSS Grid
- **Real-time Updates**: Automatic data refresh (configurable)
- **Loading States**: Visual feedback during operations

## Development

### Project Structure

```
deconz_viewer/
├── app.py              # Main application file
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── .env.example       # Environment configuration example
├── templates/         # HTML templates
│   └── index.html     # Main page template
├── static/           # Static assets
│   ├── css/
│   │   └── style.css # Application styles
│   └── js/
│       └── app.js    # Client-side JavaScript
└── README.md         # This file
```

### Running in Development

1. **Enable debug mode**:
   ```bash
   export FLASK_DEBUG=true
   python app.py
   ```

2. **Watch logs**:
   ```bash
   tail -f deconz_viewer.log
   ```

### Testing

Test the application with curl:

```bash
# Test main page
curl http://localhost:8500/

# Test API endpoints
curl http://localhost:8500/api/health
curl http://localhost:8500/api/devices
```

## Production Deployment

### Using a Production WSGI Server

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8500 app:app
```

### Environment Setup

1. **Set production environment variables**:
   ```bash
   export FLASK_DEBUG=false
   export SECRET_KEY="your-production-secret-key"
   export LOG_LEVEL=WARNING
   ```

2. **Configure logging**:
   ```bash
   export LOG_FILE=/var/log/deconz_viewer.log
   ```

## Troubleshooting

### Common Issues

1. **Database not found**:
   - Check deCONZ installation and database path
   - Verify file permissions
   - Set correct `DECONZ_DB_PATH` environment variable

2. **Port already in use**:
   - Application automatically finds free ports in range 8500-8600
   - Adjust `PORT_START` and `PORT_END` if needed

3. **Permission errors**:
   - Check file permissions for database and log files
   - Ensure write access to log directory

### Debug Mode

Enable debug mode for detailed error information:

```bash
export FLASK_DEBUG=true
export LOG_LEVEL=DEBUG
python app.py
```

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

## Changelog

### Version 2.0.0
- Complete rewrite with modern architecture
- Added API endpoints and real-time updates
- Implemented caching and performance optimizations
- Added comprehensive error handling and logging
- Modern responsive UI with CSS Grid
- Environment variable configuration
- Database connection pooling
- Enhanced security and validation

