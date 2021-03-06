##########################################################################
#
#  Copyright (c) 2014, Image Engine Design Inc. All rights reserved.
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

import Gaffer
import GafferTest

class StringAlgoTest( GafferTest.TestCase ) :

	def testMatch( self ) :

		for s, p, r in [
			( "", "", True ),
			( "a", "a", True ),
			( "a", "*", True ),
			( "ab", "a*", True ),
			( "cat", "dog", False ),
			( "dogfish", "*fish", True ),
			( "dogcollar", "*fish", False ),
			( "dog collar", "dog collar", True ),
			( "dog collar", "dog co*", True ),
			( "dog collar", "dog *", True ),
			( "dog collar", "dog*", True ),
		] :

			self.assertEqual( Gaffer.match( s, p ), r )
			if " " not in s :
				self.assertEqual( Gaffer.matchMultiple( s, p ), r )

	def testMatchMultiple( self ) :

		for s, p, r in [
			( "", "", True ),
			( "a", "b a", True ),
			( "a", "c *", True ),
			( "ab", "c a*", True ),
			( "cat", "dog fish", False ),
			( "cat", "cad cat", True ),
			( "cat", "cad ", False ),
			( "cat", "cat ", True ),
			( "cat", "cadcat", False ),
			( "dogfish", "cat *fish", True ),
			( "dogcollar", "dog *fish", False ),
			( "dogcollar", "dog collar", False ),
			( "a1", "*1 b2", True ),
		] :

			self.assertEqual( Gaffer.matchMultiple( s, p ), r )

	def testHasWildcards( self ) :

		for p, r in [
			( "", False ),
			( "a", False ),
			( "*", True ),
			( "a*", True ),
			( "a**", True ),
			( "a*b", True ),
			( "*a", True ),
		] :

			self.assertEqual( Gaffer.hasWildcards( p ), r )

if __name__ == "__main__":
	unittest.main()

