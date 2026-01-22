import asyncio
from crawl4ai import AsyncWebCrawler

async def get_startup_content(url: str) -> str:
    """
    Lance un crawler, récupère le contenu de l'URL en markdown et le nettoie.
    """
    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url, bypass_cache=True)
            
            if not result.success:
                return f"Erreur lors du crawling de {url}: {result.error_message}"
            
            # crawl4ai retourne déjà un markdown nettoyé, qui est souvent le contenu principal.
            # On retourne le markdown généré.
            return result.markdown
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Une erreur inattendue est survenue: {type(e).__name__}: {repr(e)}"
