<?xml version='1.0' encoding='UTF-8'?>
<s:schema xmlns:s="http://www.ascc.net/xml/schematron">
    <s:pattern name="verapdf-validation">

	<!--

	Manuel inspektion:
		6.1.7
		6.1.11
            	6.2.6
            	6.3.4
            	6.3.5
            	6.3.3.1
            	6.3.6
            	6.2.10
	    	6.3.2

	Afvisningsgrundlag:
		6.1.3
           	6.5.2
            	6.6.1
            	6.6.2
		6.9


<ValidationResultImpl>
  <profileDetails>
    <name>PDF/A-1B validation profile</name>
    <description>Validation rules against ISO 19005-1:2005, Cor.1:2007 and Cor.2:2011, Level B</description>
    <creator>veraPDF Consortium</creator>
    <dateCreated>1490133007707</dateCreated>
  </profileDetails>
  <totalAssertions>55358</totalAssertions>
  <pdfaflavour>PDFA_1_B</pdfaflavour>
  <compliant>false</compliant>
  <testAssertions>
    <testAssertions>
      <ordinal>19706</ordinal>
      <ruleId>
        <specification>ISO_19005_1</specification>
        <clause>6.2.3</clause>
        <testNumber>4</testNumber>
      </ruleId>
      <status>FAILED</status>

	-->

        <!-- Dismissal clauses tests -->
	<s:rule context="/ValidationResultImpl/testAssertions/testAssertions/ruleId">
            <s:assert test="not(clause = '6.1.3')">6.1.3 Is not allowed.</s:assert>
            <s:assert test="not(clause = '6.5.2')">6.5.2 Is not allowed.</s:assert>
            <s:assert test="not(clause = '6.6.1')">6.6.1 Is not allowed.</s:assert>
            <s:assert test="not(clause = '6.6.2')">6.6.2 Is not allowed.</s:assert>
            <s:assert test="not(clause = '6.9')">6.9 Is not allowed.</s:assert>
        </s:rule>
    </s:pattern>
</s:schema>

