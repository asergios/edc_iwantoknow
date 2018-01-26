<?xml version="1.0"?>
<xsl:stylesheet version="1.0"   xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                                xmlns:atom="http://www.w3.org/2005/Atom"
                                exclude-result-prefixes="atom"
>

    <xsl:template match="/">
        <ul>
            <xsl:for-each select=".//atom:entry">
                <xsl:variable name="HREF"> <xsl:value-of select="atom:link/@href"/> </xsl:variable>
                <li class="feed_content">
                    <a href= "{$HREF}"> <xsl:value-of select="atom:title"/> </a>
                </li>
            </xsl:for-each>
        </ul>
    </xsl:template>

    <xsl:output method="xml" omit-xml-declaration="yes" />

</xsl:stylesheet>