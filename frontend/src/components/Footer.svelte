<script>
    // Current year for copyright
    const currentYear = new Date().getFullYear();
</script>

<footer>
    <div class="footer-container">
        <!-- Credits -->
        <div class="credits">
            <p>Made by サラダ &copy; {currentYear}</p>
            <p class="version">v1.0.0</p>
        </div>
    </div>
</footer>

<style>
    /* Footer container */
    footer {
        text-align: center;
        padding: 1em;
        background-color: #f5f5f5;
        border-top: 1px solid #eaeaea;
        margin-top: 2rem;
    }
    
    .footer-container {
        max-width: 800px;
        margin: 0 auto;
    }

    /* Credits section */
    .credits {
        padding-top: 0.5rem;
        font-size: 0.9rem;
        color: #666;
    }
    
    .version {
        font-size: 0.8rem;
        margin-top: 0.25rem;
        color: #999;
    }
    
    /* Responsive design */
    @media (max-width: 640px) {
        .footer-container {
            padding: 0 1rem;
        }
    }
</style>
