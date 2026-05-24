export function notFoundHandler(req, res) {
  res.status(404).json({
    success: false,
    message: `Route ${req.method} ${req.originalUrl} not found`,
  })
}

export function errorHandler(error, req, res, next) {
  const statusCode = error.statusCode || 500

  res.status(statusCode).json({
    success: false,
    message: error.message || 'Internal server error',
  })
}
