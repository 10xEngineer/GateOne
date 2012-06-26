#!/usr/bin/env ruby

require 'yajl'
require 'highline/import'

puts "***"
puts "*** 10xEngineer.me lab connector"
puts "***"
puts

session_file = File.join(ENV["GO_USER_DIR"], ENV["GO_USER"], "session")

if File.exists?(session_file)
  session = Yajl::Parser.parse(IO.read(session_file))

  puts "Lab environment"
  puts
  session["lab"]["vms"].each do |vm|
    puts "\t#{vm["vm_name"]} (#{vm["vm_type"]})\t#{vm["ip_addr"]}\t#{vm["id"]}"
  end
  puts

  # TODO support vm_id passed using command line parameter
  vm_list = session["lab"]["vms"].map {|vm| vm["vm_name"]}

  target = ask("server? ") {|q| q.default = vm_list.first}

  unless vm_list.include?(target)
    puts "Invalid server!"
    sleep 10
    exit
  end

  cmd_parts = ["/opt/gateone/plugins/ssh/scripts/ssh_connect.py"]
  cmd_parts = cmd_parts + ARGV

  # TODO hardcoded user/port
  vm = session["lab"]["vms"].select {|vm| vm["alias"] == target}
  vm = vm.first

  cmd_parts << "ssh://ubuntu@#{vm["ip_addr"]}"

  cmd = cmd_parts.join(" ")

  exec cmd

  sleep 60
else
  puts "WARNING: session file not found! Try to logout."

  ask("ready?") {|q| q.default = "y"}
end

