<?xml version="1.0"?>
<xsl:stylesheet version="1.0"   xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">
    	<xsl:param name="text" select=".//pod[@id='WeatherForecast:WeatherData']/subpod/plaintext/text()"/>
    	<div class="bday-results">

			<h1>Something <xsl:value-of select="substring-before($text,'|')"/>  </h1> 
			
		</div>

    </xsl:template>

    <xsl:output method="xml" omit-xml-declaration="yes" />

</xsl:stylesheet>