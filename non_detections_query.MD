###Look for non detections
````
db.responses.find(
    {
        non_detections: {
            $not: {$size: 0}
        },
        timestamp: {
            $gt: "2015-02-12T00:00:00"
        }
    },
    {
        non_detections: 1,
        q: 1
    }
)
````