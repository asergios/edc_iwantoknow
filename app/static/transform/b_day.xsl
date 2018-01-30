<?xml version="1.0"?>
<xsl:stylesheet version="1.0"   xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">
        <div class="time_in-results">
        <h1> You were born... </h1>
                <xsl:for-each select=".//pod[@id='DifferenceConversions']//subpod">
                    <h3> <xsl:value-of select="plaintext"/> </h3>
                </xsl:for-each>
        </div>
    </xsl:template>

    <xsl:output method="xml" omit-xml-declaration="yes" />

</xsl:stylesheet>