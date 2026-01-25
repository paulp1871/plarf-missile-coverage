const express = require('express')
const app = express()

app.get('/', (req, res) => {
    res.sendFile('output/map.html' , { root : __dirname})
})

const PORT = process.env.port || 3001
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`)
})