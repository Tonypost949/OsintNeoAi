<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">


<xsl:template match="/">	

<HTML>
<HEAD>
<TITLE>Results</TITLE>
</HEAD>
  <BODY>

    <xsl:for-each select="DocumentElement/Results">

      <hr/>
      <center>
        <font face="arial" size="4" color="#FF0000">
          <strong>Result</strong>
        </font>
      </center>
      <hr/>

      <xsl:if test="InterpretationText">
        <xsl:choose>
          <xsl:when test="CompletionFlag = 'COMPLETE'">
            <font face="arial" size="2" color="#000000">
              <center>
                ********** FINAL
                <xsl:choose>
                  <xsl:when test="InterpretationTypeID = 'REPORT'"> REPORT **********</xsl:when>
                  <xsl:when test="InterpretationTypeID = 'AMENDMENT'"> AMENDMENT **********</xsl:when>
                  <xsl:when test="InterpretationTypeID = 'ADDENDUM'"> ADDENDUM **********</xsl:when>
                </xsl:choose>
              </center>
            </font>
          </xsl:when>
          <xsl:when test="InterpretationStatusID = 'APPROVED'">
            <font face="arial" size="2" color="#000000">
              <center>
                ********** FINAL
                <xsl:choose>
                  <xsl:when test="InterpretationTypeID = 'REPORT'"> REPORT **********</xsl:when>
                  <xsl:when test="InterpretationTypeID = 'AMENDMENT'"> AMENDMENT **********</xsl:when>
                  <xsl:when test="InterpretationTypeID = 'ADDENDUM'"> ADDENDUM **********</xsl:when>
                </xsl:choose>
              </center>
            </font>
          </xsl:when>
          <xsl:otherwise>
            <font face="arial" size="4" color="#FF000000">
              <center>
                ********** PRELIMINARY
                <xsl:choose>
                  <xsl:when test="InterpretationTypeID = 'REPORT'"> REPORT **********</xsl:when>
                  <xsl:when test="InterpretationTypeID = 'AMENDMENT'"> AMENDMENT **********</xsl:when>
                  <xsl:when test="InterpretationTypeID = 'ADDENDUM'"> ADDENDUM **********</xsl:when>
                </xsl:choose>
              </center>
            </font>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>

      <table border="0" cellspacing="10">
        <tr>
          <td>
            <xsl:attribute name="nowrap"/>
            <font face="arial" size="2">
              <strong>Name:</strong>
            </font>
            <font face="arial" size="2">
              <xsl:value-of select="PatientsName"/>
            </font>
          </td>
          <td>
            <xsl:attribute name="nowrap"/>
            <font face="arial" size="2">
              <strong>ID #:</strong>
            </font>
            <font face="arial" size="2">
              <xsl:value-of select="PatientID"/>
            </font>
          </td>
        </tr>

      </table>

      <xsl:if test="ErrorMessage">
        <hr/>
        <br/>
        <br/>
        <center>
          <font face="arial" size="2" color="#0000FF">
            <xsl:value-of select="ErrorMessage"/>
          </font>
        </center>
        <br/>
        <br/>
      </xsl:if>

      <table border="0" cellspacing="10">
        <tr>
          <td>
            <font face="arial" size="2">
              <xsl:choose>
                <xsl:when test="StudyDescription">
                  <strong>Exam: </strong>
                  <u>
                    <xsl:value-of select="StudyDescription"/>
                  </u>
                </xsl:when>
                <xsl:otherwise>(Procedure)</xsl:otherwise>
              </xsl:choose>
              <u>
                At <xsl:value-of select="StudyTime"/> Hours
              </u>
            </font>
          </td>
          <td>
            <font face="arial" size="2">
              <xsl:choose>
                <xsl:when test="AccessionNumber">
                  <strong>Acc#: </strong>
                  <xsl:value-of select="AccessionNumber"/>
                </xsl:when>
                <xsl:otherwise> </xsl:otherwise>
              </xsl:choose>
            </font>
          </td>
        </tr>
        <tr>
          <td>
            <xsl:attribute name="nowrap"/>
            <font face="arial" size="2">
              <strong>Exam Date:</strong>
            </font>
            <font face="arial" size="2">
              <xsl:value-of select="StudyDate"/>
            </font>
          </td>
          <td colspan="2">
            <xsl:attribute name="nowrap"/>
            <font face="arial" size="2">
              <strong>Physician:</strong>
            </font>
            <font face="arial" size="2">
              <xsl:value-of select="ReferringPhysiciansName"/>
            </font>
          </td>
        </tr>
      </table>
      <br/>
      <xsl:if test="InterpretationText">
        <br/>

        <table border="0" cellspacing="10">
          <tr>
            <td colspan="3">
              <font face="arial" size="2">
                <xsl:copy-of select="InterpretationText"/>
              </font>
            </td>
          </tr>
        </table>
        <br/>
      </xsl:if>
      <xsl:if test="InterpretationDiagnosisDescription">
        <table border="0" cellspacing="10">
          <tr>
            <td colspan="3">
              <font face="arial" size="2">
                <xsl:copy-of select="InterpretationDiagnosisDescription"/>
              </font>
            </td>
          </tr>
        </table>
        <br/>
      </xsl:if>
      <table border="0" cellspacing="10">
        <tr>
          <td colspan="3">
            <xsl:if test="Impressions">          
              <font face="arial" size="2">
                <xsl:copy-of select="Impressions"/>
              </font>
            </xsl:if>
          </td>
        </tr>
        <tr>
          <td>
            <xsl:if test="InterpretationAuthor">
              Radiologist: <xsl:value-of select="InterpretationAuthor"/>
            </xsl:if>
          </td>
        </tr>  
      </table>
    </xsl:for-each>
  </BODY>
</HTML>

</xsl:template>
</xsl:stylesheet>
