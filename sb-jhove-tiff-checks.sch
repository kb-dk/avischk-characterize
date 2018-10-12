<?xml version='1.0' encoding='UTF-8'?>
<s:schema xmlns:s="http://www.ascc.net/xml/schematron">
    <s:ns uri="http://www.loc.gov/mix/v20" prefix="mix"/>
    <s:ns uri="http://hul.harvard.edu/ois/xml/ns/jhove" prefix="jhove"/>
    <s:pattern name="jhove-tiff-validation">

	<!--
		After talking with TOES, the following technical attributes are checked:
		- Well-formedness: The tiff should be well-formed, but not necessarily valid (we have seen complaints due to invalid date seperator..)
		- Compression: Should be LZW (lossless)
		- Size: We expect a minimum size 
		- Colorspace: Should be RGB


<jhove xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://hul.harvard.edu/ois/xml/ns/jhove" xsi:schemaLocation="http://hul.harvard.edu/ois/xml/ns/jhove http://hul.harvard.edu/ois/xml/xsd/jhove/1.6/jhove.xsd" name="Jhove" release="1.20.1" date="2018-03-29">
 <date>2018-10-09T09:51:24+02:00</date>
 <repInfo uri="Kristeligt-Dagblad/KrD_TIFF/KrD_2011/20110909_00012_M_012.tiff">
  <reportingModule release="1.8" date="2017-05-11">TIFF-hul</reportingModule>
  <lastModified>2016-02-04T09:49:22+01:00</lastModified>
  <size>55530991</size>
  <format>TIFF</format>
  <version>5.0</version>
  <status>Well-Formed, but not valid</status>
  <sigMatch>
  <module>TIFF-hul</module>
  </sigMatch>
  <messages>
   <message severity="error">Invalid DateTime separator: 2016/02/04 09:45:40</message>
  </messages>
  <mimeType>image/tiff</mimeType>
  <profiles>
   <profile>DLF Benchmark for Faithful Digital Reproductions of Monographs and Serials: color</profile>
  </profiles>
  <properties>
   <property>
    <name>TIFFMetadata</name>
    <values arity="Array" type="Property">
    <property>
     <name>ByteOrder</name>
     <values arity="Scalar" type="String">
      <value>little-endian</value>
     </values>
    </property>
    .......
     <property>
       <name>Entries</name>
       <values arity="List" type="Property">
       <property>
        <name>NisoImageMetadata</name>
        <values arity="Scalar" type="NISOImageMetadata">
         <value>
       <mix:mix xmlns:mix="http://www.loc.gov/mix/v20" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/mix/v20 http://www.loc.gov/standards/mix/mix20/mix20.xsd">
        <mix:BasicDigitalObjectInformation>
         <mix:ObjectIdentifier>
          <mix:objectIdentifierType>JHOVE</mix:objectIdentifierType>
         </mix:ObjectIdentifier>
         <mix:FormatDesignation>
          <mix:formatName>image/tiff</mix:formatName>
         </mix:FormatDesignation>
         <mix:byteOrder>little endian</mix:byteOrder>
         <mix:Compression>
          <mix:compressionScheme>LZW</mix:compressionScheme>
         </mix:Compression>
        </mix:BasicDigitalObjectInformation>
        <mix:BasicImageInformation>
         <mix:BasicImageCharacteristics>
          <mix:imageWidth>4546</mix:imageWidth>
          <mix:imageHeight>6519</mix:imageHeight>
          <mix:PhotometricInterpretation>
           <mix:colorSpace>RGB</mix:colorSpace>
           <mix:ReferenceBlackWhite>
            <mix:Component>
             <mix:componentPhotometricInterpretation>R</mix:componentPhotometricInterpretation>
             <mix:footroom>



	-->

        <!-- Dismissal clauses tests -->
	<s:rule context="/jhove:jhove/jhove:repInfo/jhove:status">
		<s:assert test="starts-with(., 'Well-Formed')">TIFF file must be well-formed.</s:assert>
	</s:rule>
	<s:rule context="//mix:mix/mix:BasicDigitalObjectInformation/mix:Compression">
		<s:assert test="mix:compressionScheme = 'LZW'">Compression scheme should be LZW.</s:assert>
	</s:rule>
	<s:rule context="//mix:mix/mix:BasicImageInformation/mix:BasicImageCharacteristics">
		<s:assert test="mix:imageWidth > '1500'">Width should at least be 1500.</s:assert>
		<s:assert test="mix:imageHeight > '2500'">Height should be at least 2500.</s:assert>
	</s:rule>
	<s:rule context="//mix:mix/mix:BasicImageInformation/mix:BasicImageCharacteristics/mix:PhotometricInterpretation">
            <s:assert test="mix:colorSpace = 'RGB'">Color space should be RGB.</s:assert>
        </s:rule>
    </s:pattern>
</s:schema>

