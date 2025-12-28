module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    // Kalo udah mau dideploy, ini opsional buat nge-minify file CSS lo
    ...(process.env.NODE_ENV === 'production' ? { cssnano: {} } : {})
  },
}