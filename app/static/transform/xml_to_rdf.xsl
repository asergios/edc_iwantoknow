<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
                xmlns:foaf="http://xmlns.com/foaf/spec/"
                >


	<xsl:template match="/">
	    <rdf:RDF>
	        <xsl:apply-templates/>
	    </rdf:RDF>
	</xsl:template>


	<xsl:template match="entrie">

    	<xsl:variable name="action"><xsl:value-of select="action/text()"/></xsl:variable>

	      <rdf:Description rdf:about="http://www.entries.com/entrie/{$action}">

	        <foaf:title><xsl:value-of select="title/text()"/></foaf:title>
	        <foaf:action><xsl:value-of select="action/text()"/></foaf:action>

	        <foaf:user_inputs>

		        <rdf:Description rdf:about="http://www.user_inputs.com/{$action}">

			        <xsl:for-each select="user_inputs/user_input">

			        	<xsl:variable name="input"><xsl:value-of select="text()"/></xsl:variable>

			        	<rdf:Description rdf:about="http://www.user_inputs.com/input/{$input}">

			        		<foaf:input><xsl:value-of select="text()"/></foaf:input>
			        		<foaf:times><xsl:value-of select="@times"/></foaf:times>

			        	</rdf:Description>

			        </xsl:for-each>

			    </rdf:Description>

		    </foaf:user_inputs>

	      </rdf:Description>

  </xsl:template>



</xsl:stylesheet>