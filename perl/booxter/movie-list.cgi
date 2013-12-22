#!/usr/bin/perl -w
#
# This CGI script generates an html page from the Booxter-generated
# XML file named "MovieList.xml".
#

use CGI;
use FindBin;
use lib "$FindBin::RealBin/lib";
use XML::TreePP;

####################
# CONFIGURATION
####################

my $display_columns = {
   "Title" => "title",
   "Discs" => "numberOfMedia",
   "Genre" => "genre",
   "Series" => "series",
   "Rating" => "audienceRating",
   "Duration" => "duration",
   "Format" => "format",
};
my $default_sort = $display_columns->{"Series"};
my $column_order = [ "Title","Duration","Discs","Genre","Rating","Series","Format" ];
#my $column_order = keys %$display_columns;
my $webpage_title = "Videos (Booxter Dump)";

####################
# CGI SETUP

my $cgi = new CGI;
my $sort_order = $display_columns->{$cgi->param("sort")}; # leak?
$sort_order = $default_sort unless defined $sort_order;

my $thispage = $cgi->url(-path_info=>1);

####################
# PROCESSING

my $treepp = XML::TreePP->new();
my $hash = $treepp->parsefile( "$FindBin::RealBin/MovieList.xml" );

my $table_data = '';

my $count = 0;
my $oddity = 1;
my $rec;
$table_data .= "<tr><th>"
            . (join "</th><th>", map { "<a href=\"" . $thispage . "?sort=" . $_ . "\">" . $_ . "</a>" } @{$column_order} )
            . "</th></tr>";
foreach $rec ( sort { compare( $a, $b, $sort_order) } @{get_movies( $hash )} ) {
   $table_data .= "\n<tr class=";
   $table_data .= "\"odd\">" . build_row( $rec ) . "</tr>" if $oddity;
   $table_data .= "\"even\">" . build_row( $rec ) . "</tr>" unless $oddity;
   $oddity = ! $oddity;
   $count++;
}

####################
# SUBROUTINES

sub build_row {
   my ($record_ref) = @_;

   my $line = '';
   my $k;
   foreach $k ( @{$column_order} ) {
      $record_ref->{$display_columns->{$k}} 
         =~ s/^([a-zA-Z0-9-]+) .*$/\1/ if $k eq "Rating";
      $record_ref->{$display_columns->{$k}} 
         =~ s/ /&nbsp;/g if $k eq "Genre";
      $line .= "<td>" 
            .  normalize_generic( $record_ref->{ $display_columns->{ $k } } ) 
            .  "</td>";
   }
   return $line;
}

sub get_movies {
   my ($hash_ref) = @_;
   return $hash_ref->{"movies"}->{"movie"}; # answers an array_ref
}

sub normalize_generic {
   my ($parameter) = @_;
   return '' unless defined $parameter;
   return $parameter;
}

sub compare {
   my ( $left, $right, $column ) = @_;
   $column = $sort_order unless defined $column;

   my $a = $left->{$column};
   my $b = $right->{$column};

   # Handle undefs
   return  0 unless defined $a or defined $b;
   return -1 unless defined $a;
   return  1 unless defined $b;

   # Handle numbers
   if ( $a =~ m/^[\d]+$/ and $b =~ m/^[\d]+$/ ) {
      return $a <=> $b;
   }

   # Handle strings
   $a =~ s/^The //;
   $b =~ s/^The //;
   return $a cmp $b;
}

####################
# HTML

my $page=<<END_PAGE;
Content-Type: text/html


<html>
 <head>
  <title>$webpage_title</title>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
  <link rel="stylesheet" type="text/css" href="/movie-list.css" title="Default">
  <meta name="generator" content="Booxter/$0">
 </head>
 <body>
  <h1>Video List</h1>
  There are $count records.
  <hr>
  <table cellpadding=2 cellspacing=0>
   $table_data
  </table>
 </body>
</html>
END_PAGE

print $page;
__END__
