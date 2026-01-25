const express = require('express')
const morgan = require('morgan')
const app = express()

morgan.token('post', (req, res) => {
    return JSON.stringify(req.body)
})

const logger = morgan((tokens, req, res) => {
    const tiny = [
            tokens.method(req, res),
            tokens.url(req, res),
            tokens.status(req, res),
            tokens.res(req, res, 'content-length'), '-',
            tokens['response-time'](req, res), 'ms'
        ]
    if (req.method !== 'POST') {
        return tiny.join(' ')
    }
    return tiny.concat(tokens.post(req, res)).join(' ')
})

app.use(logger)

app.get('/', (req, res) => {
    res.sendFile('output/map.html' , { root : __dirname})
})

const PORT = process.env.port || 3001
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`)
})