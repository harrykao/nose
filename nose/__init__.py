"""nose: a discovery-based unittest extension.

nose provides an alternate test discovery and running process for
unittest, one that is intended to mimic the behavior of py.test as much
as is reasonably possible without resorting to too much magic.

Basic usage
-----------

Use the nosetests script (after installation by setuptools)::

  nosetests [options] [(optional) test files or directories]

You may also use nose in a test script::

  import nose
  nose.main()

If you don't want the test script to exit with 0 on success and 1 on failure
(like unittest.main), use nose.run() instead::

  import nose
  result = nose.run()
  
`result` will be true if the test run succeeded, or false if any test failed
or raised an uncaught exception. Lastly, you can run nose.core directly, which
will run nose.main()::

  python /path/to/nose/core.py

Please see the usage message for the nosetests script for information
about how to control which tests nose runs, which plugins are loaded,
and the test output.
  
Features
--------

Writing tests is easier
=======================

nose collects tests from unittest.TestCase subclasses, of course. But you can
also write simple test functions, and test classes that are not subclasses of
unittest.TestCase. nose also supplies a number of helpful functions for
writing timed tests, testing for exceptions, and other common use cases. See
`Writing tests`_ and `Testing tools`_ for more.

Running tests is easier
=======================

nose collects tests automatically, as long as you follow some simple
guidelines for organizing your library and test code. There's no need to
manually collect test cases into test suites. Running tests is also more
responsive, since nose begins running tests as soon as the first test module
is loaded. See `Finding and running tests`_ for more.

Setting up your test environment is easier
==========================================

nose supports fixtures at the package, module, and test case level, so
expensive initialization can be done as infrequently as possible. See
Fixtures_ for more.

Doing what you want to do is easier
===================================

nose has plugin hooks for loading, running, watching and reporting on tests
and test runs. If you don't like the default collection scheme, or it doesn't
suit the layout of your project, or you need reports in a format different
from the unittest standard, or you need to collect some additional information
about tests (like code coverage or profiling data), you can write a plugin to
do so. See `Writing plugins`_ for more.

Output capture
==============

Unless called with the -s (--nocapture) switch, nose will capture stdout
during each test run, and print the captured output only for tests that
fail or have errors. The captured output is printed immediately
following the error or failure output for the test. (Note that output in
teardown methods is captured, but can't be output with failing tests,
because teardown has not yet run at the time of the failure.)

Assert introspection
====================

When run with the -d (--detailed-errors) switch, nose will try to output
additional information about the assert expression that failed with each
failing test. Currently, this means that names in the assert expression
will be expanded into any values found for them in the locals or globals
in the frame in which the expression executed.

In other words if you have a test like::
  
  def test_integers():
      a = 2
      assert a == 4, "assert 2 is 4"

You will get output like::

  File "/path/to/file.py", line XX, in test_integers:
        assert a == 4, "assert 2 is 4"
  AssertionError: assert 2 is 4
    >>  assert 2 == 4, "assert 2 is 4"

Please note that dotted names are not expanded, and callables are not called
in the expansion.
    
Setuptools integration
======================

nose may be used with the setuptools_ test command. Simply specify
nose.collector as the test suite in your setup file::

  setup (
      # ...
      test_suite = 'nose.collector'
  )

Then to find and run tests, you can run::

  python setup.py test

When running under setuptools, you can configure nose settings via the
environment variables detailed in the nosetests script usage message.

Please note that when run under the setuptools test command, some plugins will
not be available, including the builtin coverage, profiler, and missed test
plugins.
 
nose also includes its own setuptools command, `nosetests`, that provides
support for all plugins and command line options, as well as configuration
using the setup.cfg file. See nose.commands_ for more information about the
`nosetests` command.

.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _nose.commands: #commands
.. _Writing plugins: http://code.google.com/p/python-nose/wiki/WritingPlugins

Writing tests
-------------

As with py.test, nose tests need not be subclasses of TestCase. Any function
or class that matches the configured testMatch regular expression
('(?:^|[\\b_\\.-])[Tt]est)'' by default) and lives in a module that also
matches that expression will be run as a test. For the sake of compatibility
with legacy unittest test cases, nose will also load tests from
unittest.TestCase subclasses just like unittest does. Like py.test, functional
tests will be run in the order in which they appear in the module
file. TestCase derived tests and other test classes are run in alphabetical
order.

Fixtures
========

nose supports fixtures (setup and teardown methods) at the package,
module, and test level. As with py.test or unittest fixtures, setup always
runs before any test (or collection of tests for test packages and modules);
teardown runs if setup has completed successfully, whether or not the test
or tests pass. For more detail on fixtures at each level, see below.

Test packages
=============

nose allows tests to be grouped into test packages. This allows
package-level setup; for instance, if you need to create a test database
or other data fixture for your tests, you may create it in package setup
and remove it in package teardown once per test run, rather than having to
create and tear it down once per test module or test case.

To create package-level setup and teardown methods, define setup and/or
teardown functions in the __init__.py of a test package. Setup methods may
be named 'setup', 'setup_package', 'setUp',or 'setUpPackage'; teardown may
be named 'teardown', 'teardown_package', 'tearDown' or 'tearDownPackage'.
Execution of tests in a test package begins as soon as the first test
module is loaded from the test package.

Test modules
============

A test module is a python module that matches the testMatch regular
expression. Test modules offer module-level setup and teardown; define the
method 'setup', 'setup_module', 'setUp' or 'setUpModule' for setup,
'teardown', 'teardown_module', or 'tearDownModule' for teardown. Execution
of tests in a test module begins after all tests are collected.

Test classes
============

A test class is a class defined in a test module that is either a subclass
of unittest.TestCase, or matches testMatch. Test classes that don't
descend from unittest.TestCase are run in the same way as those that do:
methods in the class that match testMatch are discovered, and a test case
constructed to run each with a fresh instance of the test class. Like
unittest.TestCase subclasses, other test classes may define setUp and
tearDown methods that will be run before and after each test method.

Test functions
==============

Any function in a test module that matches testMatch will be wrapped in a
FunctionTestCase and run as a test. The simplest possible failing test is
therefore::

  def test():
      assert False

And the simplest passing test::

  def test():
      pass

Test functions may define setup and/or teardown attributes, which will be
run before and after the test function, respectively. A convenient way to
do this, especially when several test functions in the same module need
the same setup, is to use the provided with_setup decorator::

  def setup_func():
      # ...

  def teardown_func():
      # ...

  @with_setup(setup_func, teardown_func)
  def test():
      # ...

For python 2.3, add the attributes by calling the decorator function like
so::

  def test():
      # ...
  test = with_setup(setup_func, teardown_func)(test)

or by direct assignment::

  test.setup = setup_func
  test.teardown = teardown_func
  
Test generators
===============

nose supports test functions and methods that are generators. A simple
example from nose's selftest suite is probably the best explanation::

  def test_evens():
      for i in range(0, 5):
          yield check_even, i, i*3

  def check_even(n, nn):
      assert n % 2 == 0 or nn % 2 == 0

This will result in 4 tests. nose will iterate the generator, creating a
function test case wrapper for each tuple it yields. As in the example, test
generators must yield tuples, the first element of which must be a callable
and the remaining elements the arguments to be passed to the callable.

Setup and teardown functions may be used with test generators. The setup and
teardown attributes must be attached to the generator function::

  @with_setup(setup_func, teardown_func)
  def test_generator():
      ...
      yield func, arg, arg ...

The setup and teardown functions will be executed for each test that the
generator returns.

For generator methods, the setUp and tearDown methods of the class (if any)
will be run before and after each generated test case.

Please note that method generators *are not* supported in unittest.TestCase
subclasses.

Finding and running tests
-------------------------

nose, by default, follows a few simple rules for test discovery.

* If it looks like a test, it's a test. Names of directories, modules,
  classes and functions are compared against the testMatch regular
  expression, and those that match are considered tests. Any class that is a
  unittest.TestCase subclass is also collected, so long as it is inside of a
  module that looks like a test.
   
* Directories that don't look like tests and aren't packages are not
  inspected.

* Packages are always inspected, but they are only collected if they look
  like tests. This means that you can include your tests inside of your
  packages (somepackage/tests) and nose will collect the tests without
  running package code inappropriately.

* When a project appears to have library and test code organized into
  separate directories, library directories are examined first.

* When nose imports a module, it adds that module's directory to sys.path;
  when the module is inside of a package, like package.module, it will be
  loaded as package.module and the directory of *package* will be added to
  sys.path.

Be aware that plugins and command line options can change any of those rules.   
   
Testing tools
-------------

The nose.tools module provides a number of testing aids that you may find
useful, including decorators for restricting test execution time and testing
for exceptions, and all of the same assertX methods found in unittest.TestCase
(only spelled in pep08 fashion, so assert_equal rather than assertEqual). See
`nose.tools`_ for a complete list.

.. _nose.tools: http://code.google.com/p/python-nose/wiki/TestingTools

About the name
--------------

* nose is the least silly short synonym for discover in the dictionary.com
  thesaurus that does not contain the word 'spy'.
* Pythons have noses
* The nose knows where to find your tests
* Nose Obviates Suite Employment

Contact the author
------------------

You can email me at jpellerin+nose at gmail dot com.

To report bugs, ask questions, or request features, please use the *issues*
tab at the Google code site: http://code.google.com/p/python-nose/issues/list.
Patches are welcome!

Similar test runners
--------------------

nose was inspired mainly by py.test_, which is a great test runner, but
formerly was not all that easy to install, and is not based on unittest.

Test suites written for use with nose should work equally well with py.test,
and vice versa, except for the differences in output capture and command line
arguments for the respective tools.

.. _py.test: http://codespeak.net/py/current/doc/test.html

License and copyright
---------------------

nose is copyright Jason Pellerin 2005-2007

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
"""

from nose.core import TestCollector, collector, configure, main, run, \
    run_exit, runmodule
from nose.exc import SkipTest, DeprecatedTest
from nose.loader import TestLoader
from nose.suite import LazySuite
from nose.result import TextTestResult
from nose.tools import with_setup # backwards compatibility
from nose.util import file_like, split_test_name, test_address

__author__ = 'Jason Pellerin'
__versioninfo__ = (0, 9, 2)
__version__ = '.'.join(map(str, __versioninfo__))

__all__ = [ 
    'TextTestResult', 'LazySuite', 
    'SkipTest', 'DeprecatedTest', 
    'TestCollector', 'TestLoader',
    'collector', 'configure', 'main', 'run', 'run_exit', 'runmodule',
    'with_setup', 'file_like', 'split_test_name', 'test_address'
    ]
