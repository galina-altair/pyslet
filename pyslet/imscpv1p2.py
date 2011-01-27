#! /usr/bin/env python
"""This module implements the IMS CP 1.2 specification defined by IMS GLC
"""

import pyslet.xml20081126 as xml

from types import StringTypes
from tempfile import mkdtemp
import os.path, urllib

IMSCP_NAMESPACE="http://www.imsglobal.org/xsd/imscp_v1p1"
IMSCPX_NAMESPACE="http://www.imsglobal.org/xsd/imscp_extensionv1p2"

cp_manifest=(IMSCP_NAMESPACE,'manifest')
cp_organization=(IMSCP_NAMESPACE,'organization')
cp_organizations=(IMSCP_NAMESPACE,'organizations')
cp_resource=(IMSCP_NAMESPACE,'resource')
cp_resources=(IMSCP_NAMESPACE,'resources')

cp_identifier="identifier"


class CPException(Exception): pass
class CPValidationError(CPException): pass

class CPElement(xml.XMLElement):
	"""Basic element to represent all CP elements"""  
	def __init__(self,parent):
		xml.XMLElement.__init__(self,parent)
		self.SetXMLName((IMSCP_NAMESPACE,None))


class CPManifest(CPElement):
	ID=cp_identifier
	
	def __init__(self,parent):
		CPElement.__init__(self,parent)
		self.SetXMLName(cp_manifest)
		self.organizations=CPOrganizations(self)
		self.resources=CPResources(self)

	def GetIdentifier(self):
		return self.attrs.get(cp_identifier,None)
		
	def SetIdentifier(self,identifier):
		CPElement.SetAttribute(self,cp_identifier,identifier)
		
	def GetOrganizations(self):
		return self.organizations
		
	def GetMetadata(self):
		return None
		
	def GetResources(self):
		return self.resources

	def AddChild(self,child):
		if isinstance(child,CPResources):
			self.resources=child
		else:
			CPElement.AddChild(self,child)


class CPOrganizations(CPElement):
	def __init__(self,parent):
		CPElement.__init__(self,parent)
		self.SetXMLName(cp_organizations)
		
	def AddChild(self,child):
		if isinstance(child,CPOrganization):
			CPElement.AddChild(self,child)
		elif type(child) in StringTypes:
			if child.strip():
				raise CPValidationError
		else:
			raise CPValidationError

class CPOrganization(CPElement):
	def __init__(self,parent):
		CPElement.__init__(self,parent)
		self.SetXMLName(cp_organization)
		

class CPResources(CPElement):
	def __init__(self,parent):
		CPElement.__init__(self,parent)
		self.SetXMLName(cp_resources)
		
	def AddChild(self,child):
		if isinstance(child,CPResource):
			CPElement.AddChild(self,child)
		elif type(child) in StringTypes:
			if child.strip():
				raise CPValidationError
		else:
			raise CPValidationError


class CPResource(CPElement):
	def __init__(self,parent):
		CPElement.__init__(self,parent)
		self.SetXMLName(cp_resource)
		
	
class CPDocument(xml.XMLDocument):
	def __init__(self,**args):
		""""""
		xml.XMLDocument.__init__(self,**args)
		self.defaultNS=IMSCP_NAMESPACE

	def GetElementClass(self,name):
		return CPDocument.classMap.get(name,CPDocument.classMap.get((name[0],None),xml.XMLElement))

	classMap={
		cp_manifest:CPManifest,
		cp_organizations:CPOrganizations,
		cp_organization:CPOrganization,
		cp_resources:CPResources,
		cp_resource:CPResource
		}


class ContentPackage:
	def __init__(self):
		self.CreateTempDirectory()
		self.manifest=xml.XMLDocument(root=CPManifest)
		self.manifest.SetBase(urllib.pathname2url(os.path.join(self.dPath,'imsmanifest.xml')))
		self.manifest.rootElement.SetIdentifier(self.manifest.GetUniqueID('manifest'))
		self.manifest.Create()
		
	def CreateTempDirectory(self):
		self.dPath=mkdtemp('.d','imscpv1p2-')
		