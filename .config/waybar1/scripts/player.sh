#!/bin/bash

# Get list of all active players
players=$(playerctl -l 2>/dev/null)

# Check each player
for player in $players; do
    status=$(playerctl -p "$player" status 2>/dev/null)
    
    if [ "$status" = "Playing" ]; then
        # Get metadata from this player
        artist=$(playerctl -p "$player" metadata artist 2>/dev/null)
        title=$(playerctl -p "$player" metadata title 2>/dev/null)
        station=$(playerctl -p "$player" metadata xesam:url 2>/dev/null | grep -oP '(?<=www\.|//)[^/]+' | head -1)
        
        # If it's a radio station, show station name
        if echo "$artist" | grep -qi "181\|radio\|stream\|fm"; then
            echo " $artist - $title"
        else
            echo " ${artist:0:25} - ${title:0:30}"
        fi
        exit 0
    fi
done

# Check if any player is paused
for player in $players; do
    status=$(playerctl -p "$player" status 2>/dev/null)
    if [ "$status" = "Paused" ]; then
        echo " Paused"
        exit 0
    fi
done

# No music playing
echo " No Music"
