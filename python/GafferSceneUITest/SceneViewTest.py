##########################################################################
#
#  Copyright (c) 2013, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import IECore

import Gaffer
import GafferUI
import GafferUITest
import GafferScene
import GafferSceneUI

class SceneViewTest( GafferUITest.TestCase ) :

	def testFactory( self ) :

		sphere = GafferScene.Sphere()
		view = GafferUI.View.create( sphere["out"] )

		self.assertTrue( isinstance( view, GafferSceneUI.SceneView ) )
		self.assertTrue( view["in"].getInput().isSame( sphere["out"] ) )

	def testExpandSelection( self ) :

		# A
		# |__B
		# |__C
		#    |__D
		#	 |__E

		D = GafferScene.Sphere()
		D["name"].setValue( "D" )

		E = GafferScene.Sphere()
		E["name"].setValue( "E" )

		C = GafferScene.Group()
		C["name"].setValue( "C" )

		C["in"][0].setInput( D["out"] )
		C["in"][1].setInput( E["out"] )

		B = GafferScene.Sphere()
		B["name"].setValue( "B" )

		A = GafferScene.Group()
		A["name"].setValue( "A" )
		A["in"][0].setInput( B["out"] )
		A["in"][1].setInput( C["out"] )

		view = GafferUI.View.create( A["out"] )

		def setSelection( paths ) :
			view.getContext().set(
				"ui:scene:selectedPaths",
				IECore.StringVectorData( paths ),
			)

		def getSelection() :
			return set( view.getContext().get( "ui:scene:selectedPaths" ) )

		setSelection( [ "/A" ] )
		self.assertEqual( getSelection(), set( [ "/A" ] ) )

		def setExpandedPaths( paths ) :
			view.getContext().set(
				"ui:scene:expandedPaths",
				GafferScene.PathMatcherData( GafferScene.PathMatcher( paths ) ),
			)

		def getExpandedPaths() :
			return set( view.getContext().get( "ui:scene:expandedPaths" ).value.paths() )

		setExpandedPaths( [ "/" ] )
		self.assertEqual( getExpandedPaths(), set( [ "/" ] ) )

		# expand 1 level from root

		view.expandSelection()

		self.assertEqual( getExpandedPaths(), set( [ "/", "/A" ] ) )
		self.assertEqual( getSelection(), set( [ "/A/B", "/A/C" ] ) )

		# expand one level further, from /A/B only

		setSelection( [ "/A/C" ] )

		view.expandSelection()

		self.assertEqual( getExpandedPaths(), set( [ "/", "/A", "/A/C" ] ) )
		self.assertEqual( getSelection(), set( [ "/A/C/D", "/A/C/E" ] ) )

		# do a recursive expansion from the root. all leafs should be selected.
		# leaf items should not be expanded, because there are no children to show.

		setSelection( [ "/A" ] )
		setExpandedPaths( [ "/" ] )

		view.expandSelection( depth = 3 )
		self.assertEqual( getExpandedPaths(), set( [ "/", "/A", "/A/C" ] ) )
		self.assertEqual( getSelection(), set( [ "/A/B", "/A/C/D", "/A/C/E" ] ) )

		# do an expansion where the selection is already a leaf - nothing should change

		setSelection( [ "/A/C/D" ] )

		view.expandSelection( depth = 1 )
		self.assertEqual( getExpandedPaths(), set( [ "/", "/A", "/A/C" ] ) )
		self.assertEqual( getSelection(), set( [ "/A/C/D" ] ) )

		view.expandSelection( depth = 100000000 )
		self.assertEqual( getExpandedPaths(), set( [ "/", "/A", "/A/C" ] ) )
		self.assertEqual( getSelection(), set( [ "/A/C/D" ] ) )

		# do a recursive expansion where there's an already expanded location below the selection,
		# but it's not visible because a parent isn't expanded.

		setSelection( [ "/A" ] )
		setExpandedPaths( [ "/", "/A/C" ] )

		view.expandSelection( depth = 3 )

		self.assertEqual( getExpandedPaths(), set( [ "/", "/A", "/A/C" ] ) )
		self.assertEqual( getSelection(), set( [ "/A/B", "/A/C/D", "/A/C/E" ] ) )

		# do a single level expansion where a child was previously expanded, but not visible because
		# the parent wasn't.

		setSelection( [ "/A" ] )
		setExpandedPaths( [ "/", "/A/C" ] )

		view.expandSelection()

		self.assertEqual( getExpandedPaths(), set( [ "/", "/A", "/A/C" ] ) )
		self.assertEqual( getSelection(), set( [ "/A/B", "/A/C" ] ) )

		# try to do an expansion on the leaf level - it should refuse

		setSelection( [ "/A/C/E" ] )
		setExpandedPaths( [ "/", "/A", "/A/C" ] )

		view.expandSelection()

		self.assertEqual( getExpandedPaths(), set( [ "/", "/A", "/A/C" ] ) )
		self.assertEqual( getSelection(), set( [ "/A/C/E" ] ) )

	def testLookThrough( self ) :

		script = Gaffer.ScriptNode()

		script["sphere"] = GafferScene.Sphere()
		script["camera"] = GafferScene.Camera()
		script["camera"]["transform"]["translate"].setValue( IECore.V3f( 1, 0, 0 ) )

		script["group"] = GafferScene.Group()
		script["group"]["in"][0].setInput( script["sphere"]["out"] )
		script["group"]["in"][1].setInput( script["camera"]["out"] )

		with GafferUI.Window() as window :
			viewer = GafferUI.Viewer( script )

		window.setVisible( True )

		viewer.setNodeSet( Gaffer.StandardSet( [ script["group"] ] ) )
		view = viewer.view()
		self.assertTrue( isinstance( view, GafferSceneUI.SceneView ) )

		def setViewCameraTransform( matrix ) :

			camera = view.viewportGadget().getCamera()
			camera.getTransform().matrix = matrix
			view.viewportGadget().setCamera( camera )

		def getViewCameraTransform() :

			return view.viewportGadget().getCamera().getTransform().transform()

		# Simulate the user translating the camera.
		setViewCameraTransform( IECore.M44f.createTranslated( IECore.V3f( 100, 0, 0 ) ) )
		self.assertEqual( getViewCameraTransform(), IECore.M44f.createTranslated( IECore.V3f( 100, 0, 0 ) ) )

		# Set the path for the look-through camera, but don't activate it - nothing should have changed.
		view["lookThrough"]["camera"].setValue( "/group/camera" )
		self.assertEqual( getViewCameraTransform(), IECore.M44f.createTranslated( IECore.V3f( 100, 0, 0 ) ) )

		# Enable the look-through - the camera should update.
		view["lookThrough"]["enabled"].setValue( True )
		self.waitForIdle()
		self.assertEqual( getViewCameraTransform(), script["group"]["out"].transform( "/group/camera" ) )

		# Disable the look-through - the camera should revert to its previous position.
		view["lookThrough"]["enabled"].setValue( False )
		self.waitForIdle()
		self.assertEqual( getViewCameraTransform(), IECore.M44f.createTranslated( IECore.V3f( 100, 0, 0 ) ) )

		# Simulate the user moving the viewport camera, and then move the (now disabled) look-through
		# camera. The user movement should win out.
		setViewCameraTransform( IECore.M44f.createTranslated( IECore.V3f( 200, 0, 0 ) ) )
		self.assertEqual( getViewCameraTransform(), IECore.M44f.createTranslated( IECore.V3f( 200, 0, 0 ) ) )
		script["camera"]["transform"]["translate"].setValue( IECore.V3f( 2, 0, 0 ) )
		self.waitForIdle()
		self.assertEqual( getViewCameraTransform(), IECore.M44f.createTranslated( IECore.V3f( 200, 0, 0 ) ) )

		# Change the viewer context - since look-through is disabled the user camera should not move.
		viewer.getContext().setFrame( 10 )
		self.waitForIdle()
		self.assertEqual( getViewCameraTransform(), IECore.M44f.createTranslated( IECore.V3f( 200, 0, 0 ) ) )

		# Work around "Internal C++ object (PySide.QtGui.QWidget) already deleted" error. In an
		# ideal world we'll fix this, but it's unrelated to what we're testing here.
		window.removeChild( viewer )

if __name__ == "__main__":
	unittest.main()

