<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Jobtitles extends Model
{
    Use HasFactory;
    public function employees(): HasMany
    {
        return  $this->hasMany(Employees::class);
    }
}
