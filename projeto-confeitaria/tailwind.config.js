/** @type {import('tailwindcss').Config} */
module.exports = { 
    content: ["./**/*.html"],
    theme: {
        extends: {
            colors: {
                primary: '#815a5b',
                secondary: '#f7c5c5',
                background: '#eae9dd',
                accent: '#a97c7d',
                'text-main': '#831843',
                danger: '#b91c1c',
                'danger-hover': '#991b1b',
                'text-label': '#373831',
                'text-secondary': '#52525b',
                white: '#ffffff'
            }
        }
    }
}  