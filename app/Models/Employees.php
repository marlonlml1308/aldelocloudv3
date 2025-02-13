<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Employees extends Model
{
    use HasFactory;
    public function branch(): HasMany
    {
        return  $this->hasMany(Branch::class);
    }
    public function jobtitles(): BelongsTo
    {
        return  $this->belongsTo(Jobtitles::class);
    }
}
