<?xml version="1.0"?>
<xsl:stylesheet version="1.0"   xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">

    	<div class="bday-results">
			<h1> It has about <xsl:value-of select=".//pod[@id='Result']/subpod/plaintext"/> calories! </h1> 
			<h3> <xsl:value-of select=".//pod[@id='RDVPod:Calories:ExpandedFoodData']/subpod/plaintext"/> </h3>
		</div>

    </xsl:template>

    <xsl:output method="xml" omit-xml-declaration="yes" />

</xsl:stylesheet>