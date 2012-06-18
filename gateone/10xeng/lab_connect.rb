#!/usr/bin/env ruby

require 'yajl'

puts "***"
puts "*** 10xEngineer.me lab connector"
puts "***"
puts

session_file = File.join(ENV["GO_USER_DIR"], ENV["GO_USER"], "session")

if File.exists?(session_file)
  puts "Using #{session_file}"

  session = Yajl::Parser.parse(IO.read(session_file))

  puts session.inspect
end

exec "irb"
