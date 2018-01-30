<?xml version="1.0"?>
<xsl:stylesheet version="1.0"   xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">

    	<div class="time_in-results">
    		<xsl:variable name="SRC"> <xsl:value-of select=".//pod[@id='ClockImages']/subpod/img/@src"/> </xsl:variable>

			<h1> It is 
			 <xsl:value-of select=".//pod[@id='Result']/subpod/plaintext"/> </h1>
			<h2> which gives a difference of </h2> 
			<h3> <xsl:value-of select=".//pod[@id='TimeOffsets']/subpod/plaintext"/> </h3>

			<img align="center" src="{$SRC}"/>
		</div>

    </xsl:template>

    <xsl:output method="xml" omit-xml-declaration="yes" />

</xsl:stylesheet>