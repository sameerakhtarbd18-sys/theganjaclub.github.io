<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:atom="http://www.w3.org/2005/Atom">
  <xsl:output method="html" encoding="utf-8" doctype-system="about:legacy-compat" />
  <xsl:template match="/rss/channel">
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title><xsl:value-of select="title"/> — RSS Feed</title>
        <style>
          body { font-family: 'Inter', system-ui, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; background: #fafaf9; color: #1c1917; }
          h1 { font-family: 'Fraunces', Georgia, serif; font-size: 2rem; color: #2C624A; margin-bottom: 8px; }
          p.sub { color: #78716c; margin-bottom: 32px; }
          .item { margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid #e7e5e4; }
          .item h2 { font-size: 1.25rem; margin-bottom: 6px; }
          .item h2 a { color: #1c1917; text-decoration: none; }
          .item h2 a:hover { color: #2C624A; }
          .item .date { font-size: 0.8rem; color: #a8a29e; text-transform: uppercase; margin-bottom: 8px; }
          .item p { color: #57534e; line-height: 1.6; }
          .subscribe { background: #f0fdf4; border: 1px solid #2C624A; border-radius: 8px; padding: 20px; margin-bottom: 40px; }
          .subscribe input { padding: 10px 14px; border: 1px solid #d6d3d1; border-radius: 6px; font-size: 0.9rem; width: 250px; }
          .subscribe button { padding: 10px 20px; background: #2C624A; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; margin-left: 8px; }
          a { color: #2C624A; }
        </style>
      </head>
      <body>
        <h1><xsl:value-of select="title"/></h1>
        <p class="sub"><xsl:value-of select="description"/></p>
        <div class="subscribe">
          <strong>📫 Subscribe via email</strong>
          <form action="https://buttondown.com/api/emails/embed-subscribe/theganjaclub" method="post" target="_blank" style="margin-top:12px;">
            <input type="email" name="email" placeholder="your@email.com" required />
            <button type="submit">Subscribe</button>
          </form>
        </div>
        <xsl:for-each select="item">
          <div class="item">
            <h2><a href="{link}"><xsl:value-of select="title"/></a></h2>
            <div class="date"><xsl:value-of select="pubDate"/></div>
            <p><xsl:value-of select="description"/></p>
            <small>Tags: <xsl:for-each select="category"><xsl:value-of select="."/><xsl:if test="position() != last()">, </xsl:if></xsl:for-each></small>
          </div>
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
