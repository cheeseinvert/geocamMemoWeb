#!/usr/bin/perl
# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__


use strict;
use warnings;

use File::Slurp;
use File::Basename;

my %comment = (
    ".ac"   => "dnl",
    ".am"   => "#",
    ".cc"   => "//",
    ".cpp"  => "//",
    ".cxx"  => "//",
    ".oldtest"  => "//",
    ".hpp"  => "//",
    ".cg"   => "//",
    ".glsl" => "//",
    ".h"    => "//",
    ".hh"   => "//",
    ".i"    => "//",
    ".m4"   => "dnl",
    ".mak"  => "#",
    ".pl"   => "#",
    ".py"   => "#",
    ".sh"   => "#",
    ".js"   => "//",
    ".tcc"  => "//",
    ".rst"  => "|",
    ".java" => "//",
    ".aidl" => "//",
    ".xml" => "<!--,-->",
);

my %atEnd = (
    ".rst" => 1,
);

# Read the license text from __DATA__ by default
my $f = \*DATA;
$f = $ARGV[0] if @ARGV > 0;

my @license = read_file($f);
my $shebang = '';

@license = map { chop; $_; } @license;

# process each line given on stdin
foreach my $filename (<>) {
    chomp $filename;

    # get the extension, and skip it if we don't know about it
    my (undef, undef, $ext) = fileparse($filename, qr/\.[^.]*/);

    unless (exists $comment{$ext}) {
        warn "Skipped $filename\n";
        next;
    }

    my $file = read_file($filename);

    next if ($file =~ /^\s*$/);
    next if ($file =~ /__NO_RELICENSE__/);

    $shebang = '';
    # Protect a shebang line, xml declaration, or emacs mode line
    if ($file =~ s/^(#!.*\n)//) {
        if (defined($1)) {
            $shebang = $1;
        }
    } elsif ($file =~ s/^(<\?xml.*\n)//) {
        if (defined($1)) {
            $shebang = $1;
        }
    } elsif ($file =~ s/^([^\n]*-\*-[^\n]*-\*-[^\n]*\n)//) {
        if (defined($1)) {
            $shebang = $1;
        }
    }

    # Remove a license header if it exists
    $file =~ s/^[^\n]*__BEGIN_LICENSE__.*?__END_LICENSE__[^\n]*$//ms;

    my ($chead, $ctail);
    if ($comment{$ext} =~ /,/) {
        ($chead, $ctail) = split(/,/, $comment{$ext});
        $ctail = " " . $ctail;
    } else {
        ($chead, $ctail) = ($comment{$ext}, "");
    }

    # wrapping each line of the license in the comment head and tail strings
    my $wrappedLicense = $chead . join($ctail . "\n" . $chead, @license) . $ctail;
    if ($atEnd{$ext}) {
        # Remove all blank lines from the bottom of the file
        while ($file =~ s/\s*\n$//) {};

        # append the wrapped license
        $file = $shebang . $file . "\n\n" . $wrappedLicense;
    } else {
        # Remove all blank lines from the top of the file
        while ($file =~ s/^\s*\n//) {};

        # prepend the wrapped license
        $file = $shebang . $wrappedLicense . "\n\n" . $file;
    }

    write_file($filename, $file);
}

__DATA__
 __BEGIN_LICENSE__
 Copyright (C) 2008-2010 United States Government as represented by
 the Administrator of the National Aeronautics and Space Administration.
 All Rights Reserved.
 __END_LICENSE__
