/** @type {import('tailwindcss').Config} */
module.exports = { 
    content: ["./**/*.html"],
    theme: {
        extend: {
            colors: {
                'brand-primary': '#815a5b',
                'brand-secondary': '#f7c5c5',
                'brand-background': '#eae9dd',
                'brand-accent': '#a97c7d',
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