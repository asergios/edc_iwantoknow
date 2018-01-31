<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
                xmlns:foaf="http://xmlns.com/foaf/spec/"
                xmlns:pred="http://www.entries.com/pred/"
                >


	<xsl:template match="/">
	    <rdf:RDF>
	    	<rdf:Description rdf:about="http://www.entries.com/">
	        	<xsl:apply-templates/>
	        </rdf:Description>
	    </rdf:RDF>
	</xsl:template>


	<xsl:template match="entrie">

		<pred:entrie>

    	<xsl:variable name="action"><xsl:value-of select="action/text()"/></xsl:variable>

	      <rdf:Description rdf:about="http://www.entries.com/{$action}">

	        <pred:title><xsl:value-of select="title/text()"/></pred:title>
	        <pred:action><xsl:value-of select="action/text()"/></pred:action>

	        <pred:user_inputs>

		        <rdf:Description rdf:about="http://www.entries.com/user_inputs/{$action}">

			        <xsl:for-each select="user_inputs/user_input">

			        	<xsl:variable name="input"><xsl:value-of select="text()"/></xsl:variable>
			        	<pred:user_input>
				        	<rdf:Description rdf:about="http://www.entries.com/user_inputs/{$action}/{$input}">

				        		<pred:input><xsl:value-of select="text()"/></pred:input>
				        		<pred:times><xsl:value-of select="@times"/></pred:times>

				        		<pred:result>
					        		<rdf:Description rdf:about="http://www.entries.com/result/{$action}/{$input}">
					        			<pred:expires rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">0</pred:expires>
					        		</rdf:Description>
					        	</pred:result>
					        	
				        	</rdf:Description>
				        
				        </pred:user_input>
			        </xsl:for-each>

			    </rdf:Description>

		    </pred:user_inputs>

	      </rdf:Description>

	    </pred:entrie>

  	</xsl:template>



</xsl:stylesheet>