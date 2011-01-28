#! /usr/bin/env python

import unittest
from tempfile import mkdtemp
import os, os.path, urllib, urlparse, shutil
from StringIO import StringIO


def suite():
	return unittest.TestSuite((
		unittest.makeSuite(CPTests,'test'),
		unittest.makeSuite(CPElementTests,'test'),
		unittest.makeSuite(CPManifestTests,'test'),
		unittest.makeSuite(CPDocumentTests,'test'),
		unittest.makeSuite(ContentPackageTests,'test'),
		))

from pyslet.imscpv1p2 import *

class CPTests(unittest.TestCase):
	def testCaseConstants(self):
		self.failUnless(IMSCP_NAMESPACE=="http://www.imsglobal.org/xsd/imscp_v1p1","Wrong CP namespace: %s"%IMSCP_NAMESPACE)
		self.failUnless(IMSCPX_NAMESPACE=="http://www.imsglobal.org/xsd/imscp_extensionv1p2","Wrong extension namespace: %s"%IMSCPX_NAMESPACE)

class CPElementTests(unittest.TestCase):
	def testCaseConstructor(self):
		e=CPElement(None)
		self.failUnless(e.ns==IMSCP_NAMESPACE,'ns on construction')
		
class CPXElementTests(unittest.TestCase):
	def testCaseConstructor(self):
		e=CPXElement(None)
		self.failUnless(e.ns==IMSCPX_NAMESPACE,'ns on construction')

class CPManifestTests(unittest.TestCase):
	def testCaseConstructor(self):
		m=CPManifest(None)
		self.failUnless(m.GetMetadata() is None,"Metadata present on construction")
		self.failUnless(isinstance(m.GetOrganizations(),CPOrganizations),"Organizations element required on construction")
		self.failUnless(isinstance(m.GetResources(),CPResources),"Resources element required on construction")
		self.failUnless(len(m.GetChildren())==0,"Child manifests present on construction")
		

EXAMPLE_1="""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns="http://www.imsglobal.org/xsd/imscp_v1p1" identifier="test"></manifest>"""

EXAMPLE_2="""<manifest xmlns="http://www.imsglobal.org/xsd/imscp_v1p1" xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2" 
xmlns:imsqti="http://www.imsglobal.org/xsd/imsqti_v2p1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" identifier="MANIFEST-QTI-1" 
xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd   
http://www.imsglobal.org/xsd/imsmd_v1p2 imsmd_v1p2p4.xsd  http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/imsqti_v2p1.xsd">
	<organizations/>
	<resources>
		<resource identifier="choice" type="imsqti_item_xmlv2p1" href="choice.xml">
			<metadata>
				<imsmd:lom>
					<imsmd:general>
						<imsmd:identifier>qti_v2_item_01</imsmd:identifier>
						<imsmd:title>
							<imsmd:langstring xml:lang="en">Metadata Example Item #1</imsmd:langstring>
						</imsmd:title>
						<imsmd:description>
							<imsmd:langstring xml:lang="en">This is a dummy item</imsmd:langstring>
						</imsmd:description>
					</imsmd:general>
					<imsmd:lifecycle>
						<imsmd:version>
							<imsmd:langstring xml:lang="en">1.0.1</imsmd:langstring>
						</imsmd:version>
						<imsmd:status>
							<imsmd:source>
								<imsmd:langstring xml:lang="x-none">LOMv1.0</imsmd:langstring>
							</imsmd:source>
							<imsmd:value>
								<imsmd:langstring xml:lang="x-none">Draft</imsmd:langstring>
							</imsmd:value>
						</imsmd:status>
					</imsmd:lifecycle>
					<imsmd:metametadata>
						<imsmd:metadatascheme>LOMv1.0</imsmd:metadatascheme>
						<imsmd:metadatascheme>QTIv2.1</imsmd:metadatascheme>
						<imsmd:language>en</imsmd:language>
					</imsmd:metametadata>
					<imsmd:technical>
						<imsmd:format>text/x-imsqti-item-xml</imsmd:format>
						<imsmd:format>image/png</imsmd:format>
					</imsmd:technical>
				</imsmd:lom>
				<imsqti:qtiMetadata>
					<imsqti:timeDependent>false</imsqti:timeDependent>
					<imsqti:interactionType>choiceInteraction</imsqti:interactionType>
					<imsqti:feedbackType>nonadaptive</imsqti:feedbackType>
					<imsqti:solutionAvailable>true</imsqti:solutionAvailable>
					<imsqti:toolName>XMLSPY</imsqti:toolName>
					<imsqti:toolVersion>5.4</imsqti:toolVersion>
					<imsqti:toolVendor>ALTOVA</imsqti:toolVendor>
				</imsqti:qtiMetadata>
			</metadata>
			<file href="choice.xml"/>
			<file href="images/sign.png"/>
		</resource>
	</resources>
</manifest>"""


class CPDocumentTests(unittest.TestCase):
	def testCaseConstructor(self):
		doc=CPDocument()
		self.failUnless(isinstance(doc,xml.XMLDocument))
		doc=CPDocument(root=CPManifest)
		root=doc.rootElement
		self.failUnless(isinstance(root,CPManifest))
		
	def testCaseExample1(self):
		doc=CPDocument()
		doc.Read(src=StringIO(EXAMPLE_1))
		root=doc.rootElement
		self.failUnless(isinstance(root,CPManifest))
		self.failUnless(root.ns==IMSCP_NAMESPACE and root.xmlname=='manifest')
		self.failUnless(root.GetIdentifier()=='test')
		
	def testCaseExample1(self):
		doc=CPDocument()
		doc.Read(src=StringIO(EXAMPLE_2))
		resources=doc.rootElement.GetResources()
		self.failUnless(len(resources.children)==1 and isinstance(resources.children[0],CPResource))
		manifest=doc.GetElementByID("MANIFEST-QTI-1")
		self.failUnless(doc.rootElement is manifest and isinstance(manifest,CPManifest))
		resource=doc.GetElementByID("choice")
		self.failUnless(resource is resources.children[0])
		
class ContentPackageTests(unittest.TestCase):
	def setUp(self):
		self.cwd=os.getcwd()
		self.dList=[]
		self.d=mkdtemp('.d','pyslet-test_imscpv1p2-')
		os.chdir(self.d)
		os.mkdir('package')
		os.mkdir('mpackage')
		mpath=os.path.join('mpackage','imsmanifest.xml')
		f=open(mpath,'wb')
		f.write(EXAMPLE_2)
		f.close()
		self.dList.append(self.d)
		
	def tearDown(self):
		os.chdir(self.cwd)
		for d in self.dList:
			shutil.rmtree(d,True)

	def testCaseConstructor(self):
		cp=ContentPackage()
		self.failUnless(os.path.isdir(cp.dPath),"Default constructor must create a temp directory")
		# Ensure the temporary directory is cleaned up
		self.dList.append(cp.dPath)
		url=urlparse.urlsplit(cp.manifest.GetBase())
		self.failUnless(isinstance(cp.manifest,xml.XMLDocument) and isinstance(cp.manifest.rootElement,CPManifest),"Constructor must create manifest")
		self.failUnless(os.path.split(urllib.url2pathname(url.path))[1]=='imsmanifest.xml',"Manifest file name")
		self.failUnless(isinstance(cp.manifest.rootElement,CPManifest),"Constructor must create manifest element")
		id=cp.manifest.rootElement.GetIdentifier()
		self.failUnless(cp.manifest.GetElementByID(id) is cp.manifest.rootElement,"Manifest identifief not declared")
		self.failUnless(os.path.isfile(urllib.url2pathname(url.path)),"Constructor must create manifest file")
		#print 
		#print file(urllib.url2pathname(url.path)).read()
		cp=ContentPackage('newpackage')
		self.failUnless(os.path.isdir(cp.dPath) and os.path.abspath('newpackage')==cp.dPath,"Constructor creates specified directory")
		cp=ContentPackage('package')
		self.failUnless(os.path.abspath('package')==cp.dPath,"Constructor with existing directory, no manifest")
		cp=ContentPackage('mpackage')
		self.failUnless(cp.manifest.rootElement.GetIdentifier()=="MANIFEST-QTI-1","Constructor with existing directory and manifest")
		cp=ContentPackage(os.path.join('mpackage','imsmanifest.xml'))
		self.failUnless(os.path.isdir(cp.dPath) and os.path.abspath('mpackage')==cp.dPath,"Constructor identifies pkg dir from manifest file")
		self.failUnless(cp.manifest.rootElement.GetIdentifier()=="MANIFEST-QTI-1","Constructor from manifest file")
	
	def testCaseNewResource(self):
		cp=ContentPackage('newresource')
		try:
			resource=cp.CPResource('resource#1','imsqti_item_xmlv2p1')
			self.fail("Invalid Name for resource identifier")
		except xml.XMLIDValueError:
			pass
		resource=cp.CPResource('resource_1','imsqti_item_xmlv2p1')
		self.failUnless(isinstance(resource,CPResource))
		self.failUnless(cp.manifest.GetElementByID('resource_1') is resource)
		resources=cp.manifest.rootElement.GetResources()
		self.failUnless(len(resources.children)==1 and resources.children[0] is resource)
		

if __name__ == "__main__":
	unittest.main()
